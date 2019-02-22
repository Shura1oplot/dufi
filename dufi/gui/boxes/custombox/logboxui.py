# -*- coding: utf-8 -*-

logboxui = '''\
<?xml version='1.0' encoding='utf-8'?>
<interface>
  <object class="tk.Toplevel" id="ToplevelMainWindow">
    <property name="height">200</property>
    <property name="resizable">both</property>
    <property name="width">200</property>
    <child>
      <object class="ttk.Frame" id="FrameMainWindow">
        <property name="height">200</property>
        <property name="padding">5</property>
        <property name="width">200</property>
        <layout>
          <property name="column">0</property>
          <property name="propagate">True</property>
          <property name="row">0</property>
          <property name="sticky">nsew</property>
          <rows>
            <row id="1">
              <property name="minsize">0</property>
              <property name="pad">0</property>
            </row>
            <row id="2">
              <property name="minsize">5</property>
              <property name="weight">1</property>
            </row>
            <row id="3">
              <property name="minsize">0</property>
            </row>
          </rows>
          <columns>
            <column id="0">
              <property name="weight">1</property>
            </column>
          </columns>
        </layout>
        <child>
          <object class="ttk.Label" id="LabelInfo">
            <property name="text" translatable="yes">An error (exception) has occurred in the program.
Please press Locate button to find log file displayed below and send it to the developer of this software.</property>
            <property name="textvariable">string:caption</property>
            <layout>
              <property name="column">0</property>
              <property name="propagate">True</property>
              <property name="row">0</property>
              <property name="rowspan">2</property>
              <property name="sticky">nsew</property>
            </layout>
          </object>
        </child>
        <child>
          <object class="ttk.Button" id="ButtonClose">
            <property name="command">on_button_close</property>
            <property name="text" translatable="yes">Close</property>
            <bind add="" handler="on_button_close" sequence="&lt;Return&gt;" />
            <layout>
              <property name="column">1</property>
              <property name="propagate">True</property>
              <property name="row">0</property>
              <property name="sticky">e</property>
            </layout>
          </object>
        </child>
        <child>
          <object class="ttk.Button" id="ButtonLocate">
            <property name="command">on_button_locate</property>
            <property name="text" translatable="yes">Locate</property>
            <layout>
              <property name="column">1</property>
              <property name="propagate">True</property>
              <property name="row">1</property>
              <property name="sticky">e</property>
            </layout>
          </object>
        </child>
        <child>
          <object class="pygubu.builder.widgets.scrollbarhelper" id="scrollbarhelperLog">
            <property name="scrolltype">both</property>
            <layout>
              <property name="column">0</property>
              <property name="columnspan">2</property>
              <property name="propagate">True</property>
              <property name="row">3</property>
              <property name="sticky">nsew</property>
            </layout>
            <child>
              <object class="tk.Text" id="TextLogContent">
                <property name="height">20</property>
                <property name="text" translatable="yes">01234567890123456789012345678901234567890123456789012345678901234567890123456789</property>
                <property name="width">100</property>
                <property name="wrap">word</property>
                <layout>
                  <property name="column">0</property>
                  <property name="propagate">True</property>
                  <property name="row">0</property>
                  <property name="sticky">nsew</property>
                </layout>
              </object>
            </child>
          </object>
        </child>
      </object>
    </child>
  </object>
</interface>
'''
