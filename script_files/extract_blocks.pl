#!/router/bin/perl

my @fp_blocks = `grep fp_blocks /auto/dtracker/*fp.txt`;
my $blocks;

# open each fp and extract the blocks associated with it
foreach (@fp_blocks) {
   if (/\[(.*)\]/) {
      $blocks .= $1 . ",";
      #print "$blocks\n";
   }
}
$blocks =~ s/,$//; 
#print "FPBLOCKS: @fp_blocks\n";
#print "BLOCKS: $blocks\n";

# open attributes.txt and write all the blocks extracted from fps
$^I = ".bak";
$ARGV[0] = 'attributes.txt';
while (<>) {
   s/Blocks = \[.*?\]/Blocks = \[$blocks\]/;
   print;
} 
