#!/router/bin/perl
# This script creates user files and takes in username as its parameter

use strict;
use warnings;

my $username = $ARGV[0];
my $fileType = ".txt";

# user files needed for Status Tracker
my $genReport = "statusReport_" . $username . $fileType;
my $searchResult = "searchResult_" . $username . $fileType;

system ("touch $genReport");
system ("chmod 0666 $genReport");
system ("touch $searchResult");
system ("chmod 0666 $searchResult");
