# Example time_slot values
time_slot = '3pm-4pm'
# Split the time_slot string based on the hyphen
time_parts = time_slot.split('-')
# Get the first part, which represents the start time
start_time = time_parts[0]
# Extract the first number from the start_time string
first_number = int(start_time.split('am')[0]) if 'am' in start_time else int(start_time.split('pm')[0])
print(first_number)

