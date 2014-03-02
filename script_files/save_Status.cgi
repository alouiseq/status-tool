#!/router/bin/perl
# This script creates or appends user status entries to a text file

use strict;
use warnings;
use Date::Calc qw(Month_to_Text Day_of_Week_Abbreviation Date_to_Text_Long);
use Fcntl qw (:DEFAULT :flock);
print "Content-type: text/html\n\n";

# argument should only be one and follows the following format "entry::date::attributes"
if (scalar @ARGV != 1) {
   print "User is $ENV{REMOTE_USER}\n";
   die ("ERROR- Expecting only one argument!\n");
}

my $datastr = $ARGV[0];
my $entry = "";
my $date = "";
my $attr = "";

# separate each data from argument
if ($datastr =~ /(.*?)::(.*?)::(.*)/) {     # or use split operator
   $entry = $1;
   $date = $2;
   $attr = $3;
}
#print "$entry : $date : $attr\n";

# convert numerical date from javascript date object to date string
my @datee = split " ", $date;
print "@datee\n";
my $dow = Day_of_Week_Abbreviation($datee[0]);   # returns the day of the week in string format
my $month = Month_to_Text($datee[1]+1);        # returns the month in string format
$date = $dow . " " . $month . " " . $datee[2] . " " . $datee[3] . " " . $datee[4];
#print "TEST: $date\n";

# add space between commas in attributes for readability 
$attr =~ s/,/, /g;
#print "TAGS: $attr\n";

# check to see if there is data in status report text file
# if so, then add newline to the end of output
my $checker = `wc --char statusReport.txt`;
my $empty = "\n\n";    # appended at the beginning of status entry to separate status info blocks if entries exist in file 
$checker =~ s/(\d+).*/$1/;
chomp ($checker);
unless (scalar $checker > 0) {
   $empty = "";   # if no entries present in status report file
}

# prepare a string output to write to file where username is retrieved from perl's environment user variable
my $output = $empty . "USER: " . $ENV{REMOTE_USER} . "\nDATE: " . "[" . $date . "]" . "\n" . "TAGS: " . $attr . "\n" . "ENTRY: " . $entry;
print $output; 

# create and open text file for write or if file already exists then append data to file
unless (open (TXTFILE, ">>statusEntries.txt")) {
   die ("ERROR- Cannot open textfile for write: $?");
}
# lock file (exclusive) to prevent others from modifying file at the same time
flock (TXTFILE, LOCK_EX) or die "Cannot lock file: $!\n";

# write or append data to file
print TXTFILE $output;
close(TXTFILE);    # also releases lock on file

print "\n\nCompleted\n";
