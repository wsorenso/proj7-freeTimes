import arrow
import math
class Free_Times():
	def __init__(self, busy_list):
		self.busy_list = Free_Times.copy_list(busy_list)
		self.free_list = Free_Times.between_busy(self.busy_list)
	@staticmethod
	def round_time_down(time, incr):#returns a number of minutes rounded down to nearest multiple of incr
		return incr * math.floor(1.0 * time / incr)
	@staticmethod
	def copy_list(lst):
		result = list()
		for item in lst:
			result.append( {"start": item["start"], "end": item["end"]} )
		return result
	def get_free_times(self):#returns our list of free times had self
		return self.free_list
	@staticmethod
	def normal_business_hours(start_day, end_day, daily_start_time, daily_end_time, busy_list):
		#adds times outside normal business hours to the busy list
		#this is because we don't want to meet anyone when we are off work
		#normal business hours are the range(daily_start_time, daily_end_time)
		#
		#start_day: The starting date in ISO format
		#end_day: The ending date in ISO format
		#daily_start_time: The daily start time in ISO format eg. 9:00am
		#daily_end_time: The daily end time in ISO format eg. 5:00pm
		#busy_list: The busy time list from project 6
		try:
			t_start = arrow.get(start_day)#first day in range
			t_end = arrow.get(end_day)#last day in range
			daily_tstart = arrow.get(daily_start_time)#eg. 9:00am
			daily_tend = arrow.get(daily_end_time)#eg. 5:00pm
		except:
			raise ValueError("Dates/Times are in wrong format!")
		daily_tstart = daily_tstart.floor("minute")
		#round start time down to nearest 15 min
		daily_tstart = daily_tstart.replace(minute = Free_Times.round_time_down(daily_tstart.minute, 15))
		daily_tend = daily_tend.floor("minute")
		#round end time down to nearest 15 min
		daily_tend = daily_tend.replace(minute = Free_Times.round_time_down(daily_tend.minute, 15))#round this down or up?
		startDay = t_start.floor("day")
		endDay = t_end.floor("day")
		dailyStartTime = daily_tstart.floor("minute")
		dailyEndTime = daily_tend.floor("minute")
		busy_list = Free_Times.copy_list(busy_list)#why do we need this?
		for day in arrow.Arrow.range('day', startDay, endDay):
			next_day = day.replace(days = +1)#next day
			#day will now = the moment we got off yesterday
			day = day.replace(days = dailyEndTime.day - 1, hours = dailyEndTime.hour, minutes = dailyEndTime.minute)
			#next_day will now = the time we start today
			next_day = next_day.replace(days = dailyStartTime.day - 1, hours = dailyStartTime.hour, minutes = dailyStartTime.minute)
			#add to our busy list as a busy interval
			#we were busy from when we got off work yesterday, to when we started today (day to next_day)
			busy_list.append({"start": day.isoformat(), "end": next_day.isoformat(), "desc":""})
		#unionize the busy times to consolidate overlapping intervals
		#busy_list = Free_Times.unionize( sorted( busy_list, key=lambda range: arrow.get(range["start"]).timestamp ) )
		busy_list = Free_Times.unionize(busy_list)
		return Free_Times(busy_list)#return our unionized list of busy times
	@staticmethod
	def unionize(lst):#unionizes busy times from all calendars into one set of non-overlapping busy times
		result = list()
		if len(lst) <= 0:
			return result #return an empty list
		lst = sorted(lst, key=lambda times: times["start"])#sort the list
		cur = None
		for r in lst:
			t_start = arrow.get(r["start"])#the start of a busy time
			t_end = arrow.get(r["end"])#the end of a busy time
			if cur is not None:#cur holds interval operated on last
				if cur["end"] >= t_start:#end of last busy time overlaps current start?
					if cur["end"] < t_end:#end of last busy time is before end of current?
						cur["end"] = t_end#give cur a new end time (expand interval)
					continue#go back to the top of for loop to avoid appending/changing cur
				else:#non overlapping interval
					#add interval in cur to the result since it is unique
					result.append({"start": cur["start"].isoformat(), "end": cur["end"].isoformat()})
			cur = {"start": t_start, "end": t_end}#set cur to a new busy time
		#add the final busy interval to result
		result.append({"start": cur["start"].isoformat(), "end": cur["end"].isoformat()})
		return result#non-overlapping busy times
	@staticmethod
	def between_busy(lst):#returns times we are free that fall between times we aren't
		result = list()
		if len(lst) <= 0:
			return result #an empty list
		last = None
		for cur in lst:
			if last is not None:
				#the start of our free time interval is the end of the last busy time interval
				#the end of our free time interval is the start of the current busy time interval
				result.append( {"start": last["end"], "end": cur["start"]} )#add that interval to result
			last = cur#set last to our current
		return result#return free times
	@staticmethod
	def clean_free_list(daily_start_time, daily_end_time, lst):#removes free times that are outside normal business hours
		try:
			daily_tstart = arrow.get(daily_start_time)#eg. 9:00am
			daily_tend = arrow.get(daily_end_time)#eg. 5:00pm
		except:
			raise ValueError("Dates/Times are in wrong format!")
		
		result = list()
		for cur in lst:#for each free time, make sure it doesn't start at a weird time
			if cur["start"] >= daily_tstart.isoformat():
				result.append( {"start": cur["start"], "end": cur["end"]} )#add that interval to result
		
		return result#returning free times list with no bad values

