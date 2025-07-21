# bycs_stop_class_synchronization
Stop the class syncronization

# Anleitung
1. Installiere neben python auch selenium
   'pip install selenium'
2. Create a config.ini file with the following structure and enter username, password and course_ids for which the sync of the members (class enrollment) is to be set to No. [courses] can also be omitted, but then the action takes place for all courses and this will take longer.
[login]
username = ma...
password = 123...

[mode]
headless = true
waittime = 2

[courses]
course_ids = 1681687,1681723, 1657519, 1700082, 1649545, 1631761

3. Run the script 
python ./main.py
4. Once a course has been unsynced, its ID is saved to the processed_course_ids.csv file.
5. To do it again for a course, the file should be emptied