#!/usr/bin/env perl
#Filename：amon.pl
#Author：among lifeng29@163.com 20160219
#Desc: AIX系统性能监控工具

use warnings;
use strict;
use threads;
use threads::shared;
use FindBin;
use File::Spec qw(catdir);
use lib File::Spec->catdir($FindBin::Bin,"lib");
use File::Tail;
use IO::Socket::INET;

unless ($^O eq "aix")
{
	print "not support on $^O";
	exit 1;
}

$| = 1;
my $port = 8888;
my $interval = 5;
my $nmonfile = File::Spec->catdir($FindBin::Bin,'monfile');

# res value
my $cpu:shared = "NULL";
my $mem1:shared = "NULL";
my $mem2:shared = "NULL";
my $cpu_rd:shared = "NULL";
my $mem2_rd:shared = "NULL";
my $cpu_check:shared = "NULL";
my $mem_check1:shared = "NULL";
my $mem_check2:shared = "NULL";
my $mem_tpv:shared = "NULL";

##socket server
my ($socket,$client_socket);
$socket = new IO::Socket::INET (
	LocalHost => '',
	LocalPort => $port,
	Proto => 'tcp',
	Listen => 1000,
	Reuse => 1
) or die "ERROR in Socket Creation : $!\n";

print "amon server starting up on port $port\n";

my $file = File::Tail->new(name=>$nmonfile, interval=>10, maxinterval=>5, adjustafter=>7);
my $th1 = threads->create('amon_file');
$th1->detach();
my $th2 = threads->create('run_mon');
$th2->detach();

##monitor
while (1)
{
	$client_socket = $socket->accept();
	my $data = "";
	$client_socket->recv($data,1024);
	my $res = &gen_res;
	$client_socket->send($res);
	$client_socket->close;
}
$socket->close();

sub amon_file()
{
	while (defined(my $info = $file->read))
	{
		if ($info =~ m/^CPU_ALL,T/)
		{
			my @cpu_tp = split(/,/, $info);
			$cpu_check = $cpu_tp[1];
			$cpu_rd = sprintf("%.3f",$cpu_tp[2]+$cpu_tp[3]);
			#print "CPU: $cpu_check,$cpu_rd \n";
		}
		elsif ($info =~ m/^MEM,T/)
		{
			my @mem_tp1 = split(/,/, $info);
			$mem_check1 = $mem_tp1[1];
			$mem_tpv = $mem_tp1[2];
			$mem2_rd = sprintf("%.3f",(100 - $mem_tp1[3]));
			#print "mem2: $mem_check1,$mem2_rd \n";
		}
		elsif ($info =~ m/^MEMUSE,T/)
		{
			my @mem_tp2 = split(/,/, $info);
			$mem_check2 = $mem_tp2[1];
			if (($mem_check2 eq $mem_check1) and ($mem_check2 eq $cpu_check))
			{
				$mem1 = sprintf("%.3f",(100 - $mem_tpv - $mem_tp2[2]));
				$cpu = $cpu_rd;
				$mem2 = $mem2_rd;
				#print "RES: $cpu,$mem1,$mem2";
			}
		}
		elsif ($info =~ m/^ZZZZ,T/)
		{
			$cpu = "NULL";
			$mem1 = "NULL";
			$mem2 = "NULL";
		}
		elsif ($info =~ m/ending uptime,"/)
		{
			$cpu = "NULL";
			$mem1 = "NULL";
			$mem2 = "NULL";
		}
	}
}

sub run_mon()
{
	while (1)
	{
		my $tmdf = time() - (stat $nmonfile)[9];
		if ($tmdf > (2*$interval))
		{
			my $cmd = qq(nmon -s $interval -c 9999 -F $nmonfile);
			#print "to run $cmd \n";
			system($cmd);
		}
		sleep $interval;
	}
}

sub gen_res()
{
	return <<END_TPL;
HTTP/1.0 200 OK
Date: Fri, 19 Feb 2016 01:31:10 GMT
Server: amongServer/0.1 Perl/5.10
Content-Type: text/html; charset=UTF-8

<?xml version="1.0"?>
<PerformanceMonitor>
<object class="监控类别" name="常用" desc="AIX系统常用监控项" type="ScriptMonitor">
<counter name="CPU使用率(%)" desc="CPU使用率" val="$cpu"/>
<counter name="计算内存使用率(%)" desc="计算内存使用率" val="$mem1"/>
<counter name="虚拟内存使用率(%)" desc="虚拟内存使用率" val="$mem2"/>
</object>
</PerformanceMonitor>
END_TPL
}
