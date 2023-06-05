form: "Perform ToDI resynthesis"
	# Praat requires you to add default arguments
	# but doesn't actually allow you to omit arguments
	# when calling the script, so we use empty strings.

	infile: "input_audio", ""
	infile: "input_textgrid", ""
	outfile: "output_audio", ""
	outfile: "output_image", ""
endform

if not fileReadable(input_textgrid$)
	exitScript: "input textgrid does not exist"
endif
if not fileReadable(input_audio$)
	exitScript: "input audio file does not exist"
endif

sound    = Read from file: input_audio$
textgrid = Read from file: input_textgrid$


selectObject: sound

# To Manipulation takes 3 arguments:
# Time step (s), Minimum pitch (Hz), Maximum pitch (Hz)
# We will use the default values:
manipulation = To Manipulation: 0.01, 75, 600

# Now we're gonna find the pitch tier
selectObject: textgrid

start_time = Get start time
end_time = Get end time

num_tiers = Get number of tiers
for i from 1 to num_tiers
	tier_name$ = Get tier name: i
	if tier_name$ == "ToDI-F0"
		textgrid_tier_pitch = i
	elsif tier_name$ == "duration"
		textgrid_tier_duration = i
	endif
endfor
# A pitch tier must exist
if not variableExists("textgrid_tier_pitch")
	exitScript: "`ToDI-F0' tier not found."
endif
# Duration tier is optional, so we don't check here


# Now we create the Pitch Tier from that, which we will use to replace the
# pitches of the original audio. We're also saving the max frequency,
# which we're using when we draw the resynthesized pitch.
pitch_tier = Create PitchTier: "pitch tier", start_time, end_time

max_freq = 0
selectObject: textgrid
num_pitch_points = Get number of points: textgrid_tier_pitch
for point from 1 to num_pitch_points
	selectObject: textgrid
	point_time  = Get time of point:  textgrid_tier_pitch, point
	point_freq$ = Get label of point: textgrid_tier_pitch, point
	point_freq  = number(point_freq$)

	max_freq = max(max_freq, point_freq)

	selectObject: pitch_tier
	Add point: point_time, point_freq
endfor

selectObject: manipulation, pitch_tier
Replace pitch tier


# Now we check if we have a duration tier
if variableExists("textgrid_tier_duration")
	# We'll create a Duration Tier as well
	duration_tier = Create DurationTier: "duration_tier", start_time, end_time
	selectObject: textgrid
	num_duration_points = Get number of points: textgrid_tier_duration
	for point from 1 to num_duration_points
		selectObject: textgrid
		point_time = Get time of point: textgrid_tier_duration, point
		point_speed$ = Get label of point: textgrid_tier_duration, point
		point_speed = number(point_speed$)

		selectObject: duration_tier
		Add point: point_time, point_speed
	endfor

	selectObject: manipulation, duration_tier
	Replace duration tier
endif

selectObject: manipulation
resynthesis = Get resynthesis (overlap-add)

selectObject: resynthesis
Save as WAV file: output_audio$



# Done with resynthesis; drawing

selectObject: resynthesis
Select inner viewport: 0.0, 5.5, 0.0, 1.0
# Draw sound arguments: time start (s), time end (s), amplitude min, amplitude top
# Values of zero for both time start & and, or for both amplitude min & top give the entire range
Draw: 0, 0, -1.0, 1.0, "yes", "curve"

selectObject: pitch_tier
Select inner viewport: 0.0, 5.5, 1.6, 2.6
# Draw pitch tier arguments: time start, time end, min hertz, max hertz
Draw: 0, 0, 0.0, max_freq + 25, "no", "lines and speckles"
Marks left every: 1, 50, "yes", "yes", "no"

selectObject: textgrid
Select inner viewport: 0.0, 5.5, 1.6, 2.6 + 0.25*num_tiers
Draw: 0.0, 0.0, "yes", "no", "no"
# ^ don't write the timescale, because the max time is slightly off in the case of final lengthening.
# It doesn't matter for the appearance, because the difference is milliseconds, but the difference in
# max times doesn't look nice

# That also removes the box, so we have to draw it again:
Draw inner box

Select inner viewport: 0.0, 5.5, 0.0, 2.6 + 0.25*num_tiers
Save as PDF file: output_image$
