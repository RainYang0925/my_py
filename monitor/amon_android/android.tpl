<?xml version="1.0"?>
<PerformanceMonitor>
    <object class="监控类别" name="CPU" desc="Android系统CPU监控项" type="ScriptMonitor">
        <counter name="1_Total(%)" desc="CPU总使用率" val="{{cpu_Total}}"/>
        <counter name="2_User(%)" desc="用户态的CPU使用率" val="{{cpu_User}}"/>
        <counter name="3_Sys(%)" desc="系统态的CPU使用率" val="{{cpu_Sys}}"/>
        <counter name="4_Iowait(%)" desc="IO等待的CPU使用率" val="{{cpu_iowait}}"/>
        <counter name="5_App(%)" desc="app的CPU使用率" val="{{cpu_app}}"/>
    </object>
    <object class="监控类别" name="Memory" desc="Android系统内存监控项" type="ScriptMonitor">
        <counter name="1_MemUsage(%)" desc="物理内存占用百分比" val="{{MemUsage_pct}}"/>
        <counter name="2_MemTotal(KB)" desc="系统总内存" val="{{MemTotal}}"/>
        <counter name="3_MemUsage(KB)" desc="已使用内存" val="{{MemUsage}}"/>
        <counter name="4_Buffers(KB)" desc="系统Buffer内存" val="{{Buffers}}"/>
        <counter name="5_Cached(KB)" desc="系统Cached内存" val="{{Cached}}"/>
        <counter name="6_APP Native Heap(KB)" desc="app的Native Heap内存占用(Pss)" val="{{Native_heap}}"/>
        <counter name="7_APP Dalvik Heap(KB)" desc="app的Dalvik Heap内存占用(Pss)" val="{{Dalvik_heap}}"/>
        <counter name="8_APP占用总内存(KB)" desc="APP占用总内存(Pss)" val="{{Mem_app}}"/>
    </object>
    <object class="监控类别" name="Network" desc="app流量监控项" type="ScriptMonitor">
        <counter name="1_APP下行流量占用(bytes)" desc="APP下行流量占用(bytes)" val="{{Network_rx}}"/>
        <counter name="2_APP上行流量占用(bytes)" desc="APP上行流量占用(bytes)" val="{{Network_tx}}"/>
        <counter name="3_APP总流量占用(bytes)" desc="APP总流量占用(bytes)" val="{{Network_all}}"/>
    </object>
</PerformanceMonitor>