"""Cronjob like scheduling abstraction in Python.

This module contains the functionality used by the Kodi Alarm clock
addon and is largely based on a Stackoverflow answer by
Brian on http://stackoverflow.com/questions/
373335/suggestions-for-a-cron-like-scheduler-in-python/374207#374207"""

from datetime import datetime, timedelta
import time


class CronTab(object):

    """Simulates basic cron functionality by checking for firing jobs every
    minute."""

    def __init__(self, xbmc):
        self.xbmc = xbmc
        self.jobs = []
        self.__enabled = True

    def stop(self):
        """Stops the crontab."""
        self.__enabled = False

    def start(self):
        """Starts to check every minute, if the registered jobs should run."""
        cron_time_tuple = datetime(*datetime.now().timetuple()[:5])
        while self.__enabled:
            if self.xbmc and not self.xbmc.abortRequested:
                for job in self.jobs:
                    self.xbmc.log("checking job %s against %s" %
                                  (str(job), str(cron_time_tuple)),
                                  self.xbmc.LOGDEBUG)
                    job.check(cron_time_tuple)

                cron_time_tuple += timedelta(minutes=1)
                if datetime.now() < cron_time_tuple:
                    if self.xbmc:
                        self.xbmc.sleep((cron_time_tuple -
                                         datetime.now()).seconds * 1000)
                    else:
                        time.sleep((cron_time_tuple - datetime.now()).seconds)


class AllMatch(set):

    """Universal set - match everything"""

    def __contains__(self, item):
        return True


class Job(object):
    # pylint: disable=too-many-instance-attributes,too-many-arguments
    """Cron job abstraction."""
    @staticmethod
    def conv_to_set(obj):
        """Convert obj to a set containing obj if necessary."""
        if isinstance(obj, (int, long)):
            return set([obj])
        if not isinstance(obj, set):
            obj = set(obj)
        return obj

    def __init__(self, action, minute=AllMatch(), hour=AllMatch(),
                 day=AllMatch(), month=AllMatch(), dow=AllMatch(),
                 args=(), kwargs=None):
        self.mins = Job.conv_to_set(minute)
        self.hours = Job.conv_to_set(hour)
        self.days = Job.conv_to_set(day)
        self.months = Job.conv_to_set(month)
        self.dow = Job.conv_to_set(dow)
        self.action = action
        self.args = args
        if kwargs is None:
            kwargs = {}
        self.kwargs = kwargs

    def __str__(self):
        return str(self.mins) + ", " + str(self.hours) + ", "\
            + str(self.days) + ", " + str(self.months) + ", "\
            + str(self.dow) + ", " + str(self.action) + ", "\
            + str(self.args) + ", " + str(self.kwargs)

    def is_matchtime(self, cron_time_tuple):
        """Is it the job's scheduled time"""
        return ((cron_time_tuple.minute in self.mins) and
                (cron_time_tuple.hour in self.hours) and
                (cron_time_tuple.day in self.days) and
                (cron_time_tuple.month in self.months) and
                (cron_time_tuple.weekday() in self.dow))

    def check(self, cron_time_tuple):
        """Checks if it is the scheduled time and executes the job if so."""
        if self.is_matchtime(cron_time_tuple):
            self.action(*self.args, **self.kwargs)
