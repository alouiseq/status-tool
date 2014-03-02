#!/router/bin/perl
# This script generates search results based on user's attribute and date selections

use strict;
use warnings;
use Date::Calc qw(Delta_Days Date_to_Days Add_Delta_Days Decode_Month);
use Fcntl qw (:DEFAULT :flock);
print "Content-type: text/html\n\n";

# argument should only be one and follows the following format "first_date::second_date::users::attributes//attributes..."
if (scalar @ARGV != 1) {
   die ("ERROR- Expecting only one argument: $!\n");
}

my $datastr = $ARGV[0];
my $all_dates = 1;   # default to generate report with all availabe dates
my $from_d = 0;
my $to_d = 0;
my @usr_tags = ();
my @from_date = ();
my @to_date = ();

# separate each date from argument into their respective variable
my @data_split = split (/::/, $datastr);
#print "data: @data_split\n";

# check if date range is specified, if not then generate report with all dates
if ($data_split[0] =~ /\//) {
   $all_dates = 0;    # set to 0 if user specifies a date range
   print "******************* DATE RANGE ***********************\n";
   $from_d = $data_split[0];
   $to_d = $data_split[1];
   @usr_tags = split ("//", $data_split[3]);
   #print "FROM: $from_d   TO: $to_d\n";

   # separate the FROM date to month, day, and year
   if ($from_d =~ /(\d+)\/(\d+)\/(\d+)/) {
      $from_date[0] = $1;  # month
      $from_date[1] = $2;  # day 
      $from_date[2] = $3;  # year 
   }
   else { die ("FROM date format incorrect: $!\n"); }

   # separate the TO date to month, day, and year
   if ($to_d =~ /(\d+)\/(\d+)\/(\d+)/) {
      $to_date[0] = $1;   # month
      $to_date[1] = $2;   # day 
      $to_date[2] = $3;   # year 
   }
   else { die ("TO date format incorrect: $!\n"); }

   #print "FROM: @from_date   TO: @to_date\n";
}
else {
   print "**************** ALL DATES ****************\n";
   @usr_tags = split ("//", $data_split[3]);
}
my @temp_tags = @usr_tags;   # transfer tags to a different list for temporary usage later 

# add OR/AND boolean relationship between attribute sets
my $attr = "";    # reset variable for reuse
for (my $i=0; $i < scalar @usr_tags; $i++) {
   $usr_tags[$i] =~ s/,/ || /g;
   $attr .= "(" . $usr_tags[$i] . ") && ";
}
$attr =~ s/\((\w*)\) && $/$1/;   # remove excess parenthesis and && characters
$attr =~ s/ && $//;   # remove excess && characters at the end of string
#print "TAGS: $attr\n";

# separate tags based on different attribute sets (AND relationship) and based on each attribute within a set (OR)
my @and_tags = ();
my @or_tags = ();
my @temp = "";
foreach (@temp_tags) {
   if (/,/) {
      @temp = split ",", $_;
      push @or_tags, @temp;
   }
   else {
      push @and_tags, $_;
   }
}
#print "AND:  @and_tags" . " : " . scalar @and_tags . "\n";
#print "OR:  @or_tags" . " : " . scalar @or_tags . "\n";

# check to see if there is data in status report text file
# if so, then add newline to the end of output
my $checker = `wc --char statusEntries.txt`;
my $empty = "\n\n";    # appended at the beginning of status entry to separate status info blocks if entries exist in file 
$checker =~ s/(\d+).*/$1/;
chomp ($checker);
unless (scalar $checker > 0) {
   $empty = "";   # if no entries present in status report file
}

# read status report text file and extract status information that matches user criteria 
unless (open (TXTFILE, "statusEntries.txt")) {
   die ("ERROR- Cannot open statusEntries.txt for write: $!");
}

my @buffer = <TXTFILE>;  # buffer to hold contents of status report
my $output = "";    # will hold status information with only the relevent attributes and date range
my @status_date = ();   # holds the date in month, day, and year for status entries
my $month = "";    # holds the numerical equivalence of a month in text format
my $rpt_days = "";    # holds the number equivalence of each report date
my $from_days = "";    # holds the number equivalence of the user from date
my $to_days = "";    # holds the number equivalence of the user to date
my $tag_str = "";    # holds a string of user tags
my @tags = ();      # holds a list of user tags
my %entries;	    # hash containing entries as values and order of status entries as keys
my $count = 0;      # used as keys for hash entries
my $holder = "";     # holds current line from buffer used in the foreach loop
my $key = ();      # key from hash entries
my $value = ();    # value from hash entries 
my $remote_user = $ENV{REMOTE_USER};   # authenticated user accessing web page
my $user = $data_split[2];
#print @buffer;

# tracks the number of lines in status report to ensure the last entry is included when generating report
my $num_of_elems = scalar @buffer;
my $counter = 0;
my $bool = "false";    # checks if a match is found

# iterate through the status report and match against user selected attributes assuming no date range is specified 
# uses newline character \n to identify and distinguish each entry from each other
foreach (@buffer) {
   $counter++;
   # extract and store status info including date, tags, and entry for each entry iterated
   if (($_ ne "\n") && ($counter != $num_of_elems)) {   # check to know when status entry set begins and ends 
      $holder .= $_;     # holder contains user status entry 
   }
   else {
      if ($counter == $num_of_elems) {$holder .= $_}    # ensure last line in report is included
      # loop to check for matches between user selected tags and tags in the report
      # the loop below checks for tags matching AND tags (attributes in at least two or more sets: chips, blocks, etc.)
      foreach my $and (@and_tags) {
         if ($holder =~ /$and/m) {
	    $bool = "true";  # tags matched and loop should continue for next tag check
	    next;
	 }
	 else { 
	    $bool = "false";   # match not found so end the loop
	    last; 
	 }
      }
      # if AND tags list is empty, then all tags are in OR tags list
      if (!(scalar @and_tags)) { $bool = "true"; }
      if ($bool eq "true") {     # true because AND tags are matched or no AND tags present 
	 if (scalar @or_tags) {
            foreach my $or (@or_tags) {
               if ($holder =~ /$or/m) {
                  $entries{$count} = $holder;
                  $count++;
	          last;
	       }
	    }
	 }
	 else {
            $entries{$count} = $holder;
            $count++;
         }
      }
      $holder = "";    # clear variable for the next set of status entry 
   }
} # end foreach loop

# if user selects only to view it's own status entries, then loop through the hash and remove other users' entries
if ($user eq "me") {
   while (($key, $value) = each %entries) {
      unless ($value =~ /USER:\s$remote_user/) { delete $entries{$key}; }
   }
}

# process and convert days if user selects to specify a date range for the report
if (!$all_dates) {
   $from_days = Date_to_Days($from_date[2], $from_date[0], $from_date[1]);  # convert user FROM date selection
   $to_days = Date_to_Days($to_date[2], $to_date[0], $to_date[1]);     # convert user TO selection
   #print "$from_days - $to_days\n";

   # iterate through the hash containing user entries and check against user date range specified
   while (($key, $value) = each %entries) {
      if ($value =~ /DATE:\s\[\w+ (\w+) (\d+) (\d+)/) {
	 $status_date[0] = $1;  # month
	 $status_date[1] = $2;  # day
	 $status_date[2] = $3;  # year
	 #print "Report date: @status_date\n";
	 $month = Decode_Month($status_date[0]);  # convert month in text to numerical equivalence  
	 $rpt_days = Date_to_Days($status_date[2], $month, $status_date[1]);    # from status report
    
	 # remove given key and corresponding value if entry date falls outside of user date range
	 if (($rpt_days < $from_days) || ($rpt_days > $to_days)) {
	    delete $entries{$key};
	 }
	 # print "report: $rpt_days\n";
	 # print "from: $from_days\n";
	 # print "to: $to_days\n";
      }
   } # end while loop
}

# textfile
my $myfile = "searchResult_$remote_user.txt";

# open file for write 
open (TXTFILE, "> $myfile") or die ("Cannot open statusReport.txt for write: $!"); 

# flag that indicates the first entry in hash
my $flag = 0;

# sort hash keys in descending order (newest to oldest entries) convert hash values into string
foreach $key (sort {$b <=> $a} keys %entries) {
   $output .= $entries{$key} . "\n";
   if ($flag == 0) { 
      $output .= "\n"; 
      $flag = 1;
   }
#   print "$key: $entries{$key}\n";
}
while ($output =~ /\n$/) {
   chomp($output);   # remove the last newline character from the output string
}

print "$output";
print TXTFILE $output;
close(TXTFILE);

print "\n\n***Completed***\n";
