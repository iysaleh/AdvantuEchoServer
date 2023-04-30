#!/usr/bin/env python3

import pandas

'''
Log Archive Script
    Author: Ibraheem Saleh
    Description: A simple utility that converts the EchoServer log file to a CSV format with timestamps automatically appended to the filename.
    Usage: python LogArchive.py -i EchoServer.log -o archive.log -a True
'''

"""load_data(filename)
    Loads data from a CSV file into a Pandas DataFrame.
    :param filename: The name of the file to load.
    :return: A Pandas DataFrame."""
def  load_data(filename):
    df = pandas.read_csv(filename, sep="::", names=["time","level", "logger", "message"], engine="python", header=None)
    return df

"""save_data(df, filename)
    Saves a Pandas DataFrame to a CSV file.
    :param df: The DataFrame to save.
    :param filename: The name of the file to save to.
    :return: None"""
def save_data(df, filename):
    df.to_csv(filename, sep=",", header="true", index=False)

"""save_data_json(df, filename)
    Saves a Pandas DataFrame to a JSON file.
    :param df: The DataFrame to save.
    :param filename: The name of the file to save to.
    :return: None"""
def save_data_json(df, filename):
    df.to_json(filename, orient="records", lines=True)

"""main()

    Main function that runs the script."""
if __name__ == "__main__":
    #arg parse input_file, output_file
    import sys
    import os
    #CLI Args (OptionsParser)
    import argparse
    parser = argparse.ArgumentParser(description="Log Archive Script")
    parser.add_argument("-i","--input_file", help="Input EchoServer Logfile",type=str, default="EchoServer.log")
    parser.add_argument("-o","--output_file", help="Output Archival File",type=str, default="archive.log")
    parser.add_argument("-a","--add_timestamp", help="Automatically add timestamp to output archive filename before extension",type=bool, default=True, choices=[True,False])
    parser.add_argument("-j","--json", help="Output as JSON",type=bool, default=False, choices=[True,False])
    args = parser.parse_args()
    input = args.input_file
    output = args.output_file
    add_timestamp = args.add_timestamp
    json = args.json
    #Load Data
    df = load_data(input)
    #Add Timestamp to archival filename if desired
    if add_timestamp:
        output_sep = output.split(".")
        #Get first timestamp in log for use in archival filename, remove unusable OS file characters (spaces,colons)
        first_timestamp = df.iloc[0,0].replace(" ","").replace(":","-")
        output = output_sep[0] + "." + first_timestamp + "." + output_sep[1]
    #Save Data
    print("Saving output archival file:"+output)
    if json:
        save_data_json(df, output)
    else:
        save_data(df, output)