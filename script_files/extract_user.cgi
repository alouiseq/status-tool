#!/router/bin/perl
# This script simply uses environment user variable to retrieve user accessing the server

print "Content-type: text/html\n\n";
use strict;
use warnings;

# retrieve user name from perl's environment variable
my $remote_user = $ENV{REMOTE_USER};
print $remote_user;
