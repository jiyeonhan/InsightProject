#!/usr/bin/env python
#
# read a root tree using Pyroot and find muon track
#
#
import os

import sys, uuid

import operator
import datetime

from operator import itemgetter


def write_file(sort_title, sort_list, output):
    #Write the sorted information to the file(output)
    #arg : sort_title (title for output index), sort_list (list of sorted iinformation), output (output file)
    out_file = open(output, "w")

    out_file.write(sort_title+"\n")
    for ni in range(len(sort_list)):
        out_line = sort_list[ni][0]+";"+str(sort_list[ni][1])+";"+"%0.1f" % (sort_list[ni][2]*100.0)+"%"
        out_file.write(out_line+"\n")

    out_file.close()


def split_outside_of_quotes(line_string):
    #Split the information based on semi-colon excluding quoted string (single quoted string is not considered)
    arr = []
    start, flag = 0, False

    for pos, x in enumerate(line_string):        
        if x == '"':
            flag= not(flag)
        if flag == False and x == ';':
            arr.append(line_string[start:pos])
            start = pos+1

    arr.append(line_string[start:pos])
    return arr


def save_info(input_txt, strip):
    #Read the input file and extract the necessary information (strip) to process the project
    strip_pair = {}
    visa_app=[]

    title_line = True
    with open(input_txt) as f:
        for line in f:
            line_name = line.rstrip()

            # The first line saves the title of application contents. Matching the index number for "strip" variables
            if title_line is True:  
                info = line_name.split(";")
                info[0] = "INDEX"

                for s in strip:
                    for i in info:
                        if s in i:
                            strip_pair.update({i:info.index(i)})
                            continue
                title_line = False
            else:
                #Separate string line using semi-colon (excluding quoted string)
                val = split_outside_of_quotes(line_name)        

                ind_info={}
                try:
                    for k, v in strip_pair.items():
                        ind_info.update({k:val[v].replace('"','')})
                except ValueError:
                    print("Can not save info.")

                visa_app.append(ind_info)

    f.close()

    return visa_app


def status_count_with_sorting(app, tag):
    #Return whole list of the occupations(or states) checking case status and the rate of certified status
    #Return top 10 sorted information using sorting function defined in the code

    #Find the index name of tag and status in the dataset
    # Make sure if tag and "STATUS" is in title index, if the naming is not same, update it
    tag_title = [x for x in app[0].keys() if tag in x][0]  
    status_title = [x for x in app[0].keys() if "STATUS" in x][0]

    #Define dictionary of the case status for the target item
    #Count "CERTIFIED" only vs. others ("CERTIFIED-WITHDRAWN"/"WITHDRAWN"/"DENIED")
    #Relative certification rate in the occupancy (Ncert/(Ncert+Nfail)) in category is also interesting
    occp={}
    for ai in app:
        status = 1 if ai[status_title] == "CERTIFIED" else 0
        if ai[tag_title] in occp.keys():
            occp[ai[tag_title]] += status

        else:
            occp.update({ai[tag_title]:status})

    #Count the total number of "CERTIFIED" (tcert)
    tcert = sum([v for v in occp.values()])

    #Calculate the fraction of "CERTIFIED" case to the total "CERTIFIED" case and save in the list
    occp_list = []
    for k, v in occp.items():
        frac = float(v)/float(tcert)
        occp_list.append([k, v, frac])

    #Sorting information by the number of "CERTIFIED" case, and then alphabetically of occupations or states
    ntop = 10 if len(occp_list)>10 else len(occp_list)
    occp_list_top10 = sorted( occp_list, key=operator.itemgetter(1), reverse=True )[0:ntop]
    occp_sort = sorting(occp_list_top10)  

    return occp_sort


def sorting(occp_list):
    #Sorting the information :
    #First identifier of sorting is the second index, the number of certified applications (reverse order)
    #In the case of a tie, sort alphabetically of first index (top occupations or top states in the project)

    for it in range(len(occp_list)-1, 0, -1):
        for ix in range(it):
            if occp_list[ix][1]<occp_list[ix+1][1]:
                occp_list[ix], occp_list[ix+1] = occp_list[ix+1], occp_list[ix]
            elif occp_list[ix][1]==occp_list[ix+1][1]:
                if occp_list[ix][0]>occp_list[ix+1][0]:
                    occp_list[ix], occp_list[ix+1] = occp_list[ix+1], occp_list[ix]

    return occp_list




if __name__ == '__main__':

    start_time = datetime.datetime.now()

    #Assign the input and output files
    fname = sys.argv[1]
    out_fname = [sys.argv[2], sys.argv[3]]

    #If input file doesn't exist, stop processing
    if os.path.exists(fname) is False:
        print("No input file exists : %s" % fname)
        ifname = fname.split("/")[-1]
        fname = "../input/"+ifname if os.path.exists("../input/"+ifname) else sys.exit(0)
        
    #If output directory defined as an input argument doesn't exist, save output file in output directory
    # using relative location to src area 
    for ofile in out_fname:
        ofname = ofile.split("/")[-1]
        odir = ofile[:len(ofile)-len(ofname)]
        if os.path.isdir(odir) is False:
            cwd = os.getcwd()            
            out_fname[out_fname.index(ofile)] = "../output/"+ofname


    print("Input file = %s" % fname)
    print("Output file = %s, %s" % (out_fname[0], out_fname[1]))

    #Assign the target information and title which needs to be listed
    target = ["SOC_NAME", "WORKSITE_STATE"]
    target_title = ["TOP_OCCUPATIONS;NUMBER_CERTIFIED_APPLICATIONS;PERCENTAGE", "TOP_STATES;NUMBER_CERTIFIED_APPLICATIONS;PERCENTAGE"]
    strip = ["SOC_CODE", "STATUS"]

    #Change "WORKSITE_STATE" index title for FY_2014 case. Only consider the primary work location
    #It might not be necessary if the user considers the right target naming depending on the dataset
    if "FY_2014" in fname:
        target[1] = "LCA_CASE_WORKLOC1_STATE"

    #Add necessary information for the project processing
    strip += target

    #Read the input file and save the necessay information (strip variable) using dictionary
    #: key(applicant info. item), value(applicant's information)
    app = save_info(fname, strip)

    #Run the sorting algorithm for the target and write information to the output file
    for t in range(len(target)):    
        occp_sort = status_count_with_sorting(app, target[t])
        write_file(target_title[t], occp_sort, out_fname[t])

    end_time = datetime.datetime.now()
    time_diff = end_time - start_time
    print "Processing time for the project = ",  time_diff

        
