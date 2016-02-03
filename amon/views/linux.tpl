<?xml version="1.0"?>
<PerformanceMonitor>
<object class="监控类别" name="常用" desc="Linux系统常用监控项" type="ScriptMonitor">
<counter name="CPU使用率" desc="CPU使用率" val="{{cpu_Total}}"/>
<counter name="内存使用率" desc="物理内存使用率" val="{{MemUsage_pct}}"/>
</object>
<object class="监控类别" name="CPU" desc="Linux系统CPU监控项" type="ScriptMonitor">
<counter name="1_Total(%)" desc="CPU总使用率" val="{{cpu_Total}}"/>
<counter name="2_User(%)" desc="用户态的CPU使用率" val="{{cpu_User}}"/>
<counter name="3_Sys(%)" desc="系统态的CPU使用率" val="{{cpu_Sys}}"/>
<counter name="4_Iowait(%)" desc="IO等待的CPU使用率" val="{{cpu_iowait}}"/>
</object>
<object class="监控类别" name="Memory" desc="Linux系统内存监控项" type="ScriptMonitor">
<counter name="3_MemTotal(KB)" desc="系统总内存" val="{{MemTotal}}"/>
<counter name="4_MemUsage(KB)" desc="已使用内存" val="{{MemUsage}}"/>
<counter name="5_Buffers(KB)" desc="系统Buffer内存" val="{{Buffers}}"/>
<counter name="6_Cached(KB)" desc="系统Cached内存" val="{{Cached}}"/>
<counter name="7_SwapTotal(KB)" desc="Swap总大小" val="{{SwapTotal}}"/>
<counter name="8_SwapUsage(KB)" desc="Swap已使用大小" val="{{SwapUsage}}"/>
<counter name="1_MemUsage(%)" desc="物理内存占用百分比" val="{{MemUsage_pct}}"/>
<counter name="2_SwapUsage(%)" desc="Swap占用百分比" val="{{SwapUsage_pct}}"/>
</object>
</PerformanceMonitor>