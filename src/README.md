
# Problem

  The source code (h1b_counting.py) reads the input file defined in run.sh and returns two output file, top 10 occupation names list (associated with SOC_CODE) and top 10 states list in the output file under ../output/ directory.
  The output file contains top 10 occupations (or states) with the number of the certified applications and its fraction to total  certified applications regardness of occupations (or states).


# Approach
 1) Read input file as a string and split the contents based on semi-colon (ignore semi-colon inside of the quoted string)

 2) Save application information as a dictionary (key:index title, value:application info for the index title)
    : can only save the selective information defined in strip and target list in main function

 3) Count "CERTIFIED" case only and then calculate the fraction of "CERTIFIED" case to the total number of "CERTIFIED" applications

 4) Sorting the occupation names (or states) by the number of "CERTIFIED" status and save top 10 list, 
    and then rerun the sorting function to sort for the second criteria, in case of a tie, order alphabetically by the occupation names (or states)

 5) Write the information to the output file



# Code structure
  
  -Function list

    def write_file(sort_title, sort_list, output): 
       Write "sort_title" and "sort_list" to the output file
       "sort_title" : the index title for the output file
       "sort_list"  : the sorted list of applications
       "output"     : the output file location and name
    	 
    def split_outside_of_quotes(string):
    	Split the string based on semi-colon excluding the semi-colon inside of the quoted string
	Return the list of splitted information

    def save_info(input_txt, strip):
    	Read input text file and then save the information for "strip" list
	"input_txt" : input file to save the applications as a text file (.csv format)
	"strip"  : list of index title to be saved
	Return the list of applications, its individual information is saved as a dictionary (key: index title, value: info. of application)

    def status_count_with_sorting(app, tag):
    	Save the list of the occupation names (or states) with the number of "CERTIFIED" case and it's rate to the total, and then sort top 10 list 
	"app" : returned list of applications from "save_info" function
	"tag" : the item title to be sorted
	Retun top 10 list of applications sorted by the number of "CERTIFIED" case [ occupation names or states, N("CERTIFIED"), Fraction of N("CERTIFIED") to the total "CERTIFIED" case]

    def sorting(occp_list):
    	Sorting the information by the number of "CERTIFIED" applications, and in case of a tie, alphabetically of occupation name (or states)
	"occp_list" : List of applications to be sorted 
	Return the sorted list

  
 
# Instructions : argument setting in main function

    * Three arguments : sys.argv[1] is the input file
                        sys.argv[2] is the output file for top 10 occupations list
                        sys.argv[3] is the output file for top 10 states list

    * target = [] : Save target item to be saved in the output file.
                    For this project, the target is "SOC_NAME" and "WORKSITE_STATES".
      	       	    For FY_2014, "WORKSITE_STATE" is saved as "LCA_CASE_WORKLOC1_STATE" and "LCA_CASE_WORKLOC2_STATE".
                    In the code, only primary work location ("LCA_CASE_WORKLOC1_STATE") is considered for 2014.
		    If the index title format is not similar, need to change the target info.
    
    * target_title = [] : Update target_title based on target choice.

    * strip = [] : List the index title which needs to be saved on top of target infomation.
      	      	   The target list is added to strip list      	      	    


    REMARK) The index title of FY_2014 dataset seems to be much different from FY_2015 and FY_2015 data format.
	    In this case, the user need to define the exact index title name in "target" list






