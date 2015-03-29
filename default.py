"""Startup script for the Kodi alarm clock add-on."""
# pylint: disable=import-error
import xbmc
import xbmcaddon
import os
import sys

__cwd__ = xbmc.translatePath(
    xbmcaddon.Addon().getAddonInfo('path')).decode("utf-8")
__resource__ = xbmc.translatePath(
    os.path.join(__cwd__, 'resources', 'lib')).decode("utf-8")
sys.path.append(__resource__)
from cronjobs import CronTab, Job


class AlarmClock(object):

    """Main alarm clock application class."""

    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.crontab = CronTab(xbmc)

    def apply_settings(self):
        """Gets the current configuration and updates the scheduler."""
        self.addon = xbmcaddon.Addon()
        self.crontab.jobs = self._get_alarms()

    def start(self):
        """Starts the alarm clock, ie. activates the defined alarms."""
        self.crontab.start()

    def stop(self):
        """Stops the alarm clock."""
        self.crontab.stop()

    def _get_alarms(self):
        """Get a list of the cron jobs for the enabled alarms."""
        jobs = []

        for i in range(1, 6):
            if self.addon.getSetting("alarm%d" % i) == "true":
                jobs.extend(self._get_jobs(i))
        xbmc.log("events fetched: %s" % str(jobs), xbmc.LOGDEBUG)
        return jobs

    def _get_jobs(self, number):
        """Initialize jobs(s) for alarm number.
        If the alarm has a duration enabled, both the start and the stop job
        are returned in the list."""
        days_of_week = int(self.addon.getSetting("day%d" % number))
        if days_of_week == 7:
            days_of_week = range(5)
        if days_of_week == 8:
            days_of_week = range(7)

        action = self.addon.getSetting("action%d" % number)
        if action == "0":
            file_name = self.addon.getSetting("file%d" % number)
        else:
            file_name = self.addon.getSetting("text%d" % number)

        jobs = [Job(self._start_playing,
                    int(self.addon.getSetting("minute%d" % number)),
                    int(self.addon.getSetting("hour%d" % number)),
                    dow=days_of_week,
                    args=[file_name, self.addon.getSetting("volume%d" %
                                                           number)])]

        if self.addon.getSetting("turnOff%d" % number) == "true":
            jobs.append(Job(self._stop_playing,
                            int(self.addon.getSetting("minute%d" % number)) +
                            (int(self.addon.getSetting("duration%d" %
                                                       number)) % 60),
                            int(self.addon.getSetting("hour%d" % number)) +
                            (int(self.addon.getSetting("duration%d" %
                                                       number)) / 60),
                            dow=days_of_week))
        return jobs

    def _start_playing(self, item, volume):
        """Starts playing the given item at the supplied volume."""
        try:
            xbmc.executebuiltin('CECActivateSource')
        # pylint: disable=broad-except
        except Exception:
            xbmc.log("CECActivateSource not supported", xbmc.LOGDEBUG)

        xbmc.executebuiltin('SetVolume(%s)' % volume)
        xbmc.Player().play(item)

    def _stop_playing(self):
        """Stops whatever is playing at the moment"""
        xbmc.Player().stop()


class AlarmClockMonitor(xbmc.Monitor):

    """Monitor subclass listening on configuration changes and termination
    requests."""
    # pylint: disable=missing-docstring,invalid-name
    def __init__(self, alarm_clock):
        xbmc.Monitor.__init__(self)
        self.alarm_clock = alarm_clock
        self.alarm_clock.apply_settings()

    def onSettingsChanged(self):
        self.alarm_clock.apply_settings()

    def onAbortRequested(self):
        self.alarm_clock.stop()


def main():
    """Main function setting up the addon"""
    alarm_clock = AlarmClock()
    AlarmClockMonitor(alarm_clock)
    xbmc.log("Starting alarm clock..", xbmc.LOGDEBUG)
    alarm_clock.start()

if __name__ == '__main__':
    main()
