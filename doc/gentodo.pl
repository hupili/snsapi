#!/usr/bin/env perl

use strict;
use warnings;
use FindBin qw($Bin $Script) ;
our $fn_execute = "$Bin/$Script" ;
our $dir_execute = $Bin ;

our $dir_project = "$dir_execute/../" ;
our @a_ext = ("*.py", "*.pl", "*.sh") ;
our @a_avoid = ("^./doc", "/back/", "/third/") ;
our $count_todos = 0 ;

sub print_preamble {
	print qq(<link tpye='text/rss' href="http://personal.ie.cuhk.edu.hk/~hpl011/css/markdown.css" rel="stylesheet"/>\n) ;
	print "<h1> TODOs of SNSAPI (from Code) </h1>" ;
	#print "# TODOs of SNSAPI (from Code)" ;
}

sub format_todo_block {
	my ($fn, $no, $text) = @_ ;
	#print qq(## "$fn" : line $no) ;
	#print "\n```\n$text\n```\n" ;
	$count_todos ++ ;
	print qq(<h2> $count_todos. "$fn" : line $no </h2>\n) ;
	print "\n<pre><code>\n$text\n</code></pre>\n" ;
}

sub parse_todo_block {
	my ($fn) = @_ ;
	#print $fn ;
	open f_code, "< $dir_project/$fn" or die("can not open: $fn") ;
	my $in_todo = 0 ;
	my $no = 0 ;
	my $text = "" ;
	while (my $line = <f_code>) {
		$no ++ ;
		if ( !$in_todo ) {
			if ($line =~ /^\s*#+\s*TODO/) {
				$in_todo = 1 ;
			}
		} 
		if ($in_todo){
			if ($line =~ /^\s*#/) {
				$line =~ s/^\s*//g ;
				$text .= $line ;
			} else {
				$in_todo = 0 ;
				format_todo_block($fn, $no, $text) ;
				$text = "" ;
			}
		}
	}
	close f_code ;
}

sub main {
	print_preamble() ;
	my @a_fn = () ;
	for my $ext(@a_ext){
		push @a_fn, `cd $dir_project; find . -name "$ext"` ;
	}
	#print "@a_fn" ;
	for my $fn(@a_fn){
		chomp $fn ;
		my $skip = 0 ;
		for my $pattern(@a_avoid){
			if ( $fn =~ /$pattern/ ){
				$skip = 1 ;
				last ;
			}
		}
		if ( ! $skip ){
			parse_todo_block($fn) ;
		}
	}
}

# ==== main ====

main() ;

exit 0 ;
