# Overview of Wiser Home Assistant Integration Services

This integration supports many services, whether existing HA services or specific custom ones to allow control of your Wiser system in automations.

The following sets out how to use the custom Wiser services and the supported built in HA ones.

It is highly recommended to use the Developer Tools in HA to develop the YAML for your service call if you are not sure.  Most of the services will give helpful guidance through this tool to correctly configure.

Please feel free to correct any errors or omissions by posting a PR to our Github.

## Contents

### Wiser Custom Services
- [Boost Heating](#boost-heating)
- [Boost Hot Water](#boost-hot-water)
- [Set Device Mode](#set-device-mode)
- [Save Schedule to File](#save-schedule-to-file)
- [Set Schedule from File](#set-schedule-from-file)
- [Copy Schedule](#copy-schedule)
- [Assign Schedule](#assign-schedule)

### Supported HA Built In Services
- [Climate Services](#climate-services)
- [Switch Services](#switch-services)
- [Select Services](#select-services)
- [Button Services](#button-services)
- [Light Services](#light-services-eu-hub-only)
- [Cover Services](#cover-services-eu-hub-only)

&nbsp;
# Wiser Custom Services

## Boost Heating
**Service Name**: wiser.boost_heating

**Target**: Any wiser climate entity

There are 2 options for this service (both require a duration value):
1) Boost the temperature by an increase amount from the current room temperature for a period of time

    ```
    service: wiser.boost_heating
    data:
        time_period: 60
        temperature_delta: 2
    target:
        entity_id: climate.wiser_kitchen
    ```

2) Set the temperature to a specific target for a period of time

    ```
    service: wiser.boost_heating
    data:
        time_period: 60
        temperature: 22
    target:
        entity_id: climate.wiser_kitchen
    ```
#
## Boost Hot Water
**Service Name**: wiser.boost_hotwater

Turn the hotwater on for a specified amount of time.  This overrides the schedule or manual setting but if after the set duration the schedule or manual setting is on, the hotwater will continue to be on.

**NOTE**: If you have more than 1 wiser hub setup with this integration, you will need to also specify which hub you wish to boost or it will give you an error.

1) Single hub only

    ```
    service: wiser.boost_hotwater
    data:
        time_period: 60
    ```

2) Multiple hubs
    
    ```
    service: wiser.boost_hotwater
    data:
        time_period: 60
        hub: WiserHeatXXXXXX
    ```

#
## Set Device Mode
**Service Name**: wiser.set_device_mode

Set the mode of a smartplug, hotwater, lights or shutters between Auto (follow schedule) or Manual (do not follow schedule)

**NOTE**: This is the same as the select.select_option service built into HA but has UI helpers if used in the development tools.

```
service: wiser.set_device_mode
data:
entity_id: select.wiser_smartplug1_mode
mode: Auto
```

#
## Save Schedule to File
**Service Name**: wiser.get_schedule

Output the schedule from the wiser hub into a yaml formatted file.  This can then be amended or used in automations to set different schedules based on time of year etc.

**Parameters**

- **Entity**: Any climate entity for rooms or any mode select entity for smartplugs, hot water, lights or shutters.  You can supply multiple entities to save each to a file.  If you do this, do not provide a filename.

- **Filename**: The filename of the file to save the schedule to.  If not provided, it will be stored in /config/schedules/schedule_[room/device name].yaml


1) Climate Entity
    ```
    service: wiser.get_schedule
    data:
        entity_id: climate.wiser_kitchen
    ```
    ```
    service: wiser.get_schedule
    data:
        entity_id: climate.wiser_kitchen
        filename: /config/kitchen.yaml
    ```

2) Non Climate Entity (Smart Plugs, Hot Water, Lights, Shutters)
    ```
    service: wiser.get_schedule
    data:
        entity_id: select.wiser_hot_water_mode
    ```
    ```
    service: wiser.get_schedule
    data:
        entity_id: select.wiser_hot_water_mode
        filename: /config/hw.yaml
    ```

2) Multiple Entities
    ```
    service: wiser.get_schedule
    data:
        entity_id: 
            - climate.wiser_dining_room
            - climate.wiser_kitchen
            - climate.wiser_lounge
    ```

#
## Set Schedule from File
**Service Name**: wiser.set_schedule

**Entity**: Any climate entity or any mode select entity for smartplugs, hot water, lights or shutters.  You can select multiple entities and load the same schedule to each.

**Filename**: The filename of the file to set the schedule from.  Should be the full path including i.e. /config/schedules/kitchen.yaml

Load a schedule into the wiser hub from a yaml formatted file.  This can be used in automations to set different schedules based on time of year etc from different files.

1) Climate Entity
    ```
    service: wiser.set_schedule
    data:
        entity_id: climate.wiser_kitchen
        filename: /config/kitchen.yaml
    ```

2) Non Climate Entity (Smart Plugs, Hot Water, Lights, Shutters)
    ```
    service: wiser.set_schedule
    data:
        entity_id: select.wiser_hot_water_mode
        filename: /config/hw.yaml
    ```

3) Multiple Entities
    ```
    service: wiser.set_schedule
    data:
        entity_id: 
            - climate.wiser_dining_room
            - climate.wiser_kitchen
            - climate.wiser_lounge
        filename: config/schedules/summer_schedule.yaml
    ```

#
## Copy Schedule
**Service Name**: wiser.copy_schedule

Copy schedules between rooms/devices.

**Entity**: Any climate entity or any mode select entity for smartplugs, hot water, lights or shutters

**To Entity**: Any climate entity or any mode select entity for smartplugs, hot water, lights or shutters


**NOTE**: There are a number of requirements that have to be met and are validated by this service call.  You will get an error if any are not met.

- The 2 entites must already have schedules assigned to them

- The 2 entities must be of the same time i.e:
    - climate to climate
    - smart plug to smart plug
    - light to light
    - shutter to shutter

- If you have more than one hub, the entities must be from the same hub.  To copy between hubs use the get_schedule and set_schedule services.

```
service: wiser.copy_schedule
data:
    entity_id: climate.wiser_kitchen
    to_entity_id: climate.wiser_lounge
```


#
## Assign Schedule
**Service Name**: wiser.assign_schedule

**Entity**: Any climate entity or any mode select entity for smartplugs, hot water, lights or shutters

**Schedule ID**: An id of a suitable schedule type for the To Entity.  The schedule ID can be found on the attributes of an Entity

**To Entity**: Any climate entity or any mode select entity for smartplugs, hot water, lights or shutters

**NOTES**: 
1) The wiser hub can have the same schedule assigned to multiple rooms/smart plugs/lights/shutters etc.

2) There are a number of requirements that have to be met and are validated by this service call.  You will get an error if any are not met.

    - The 'from' Entity must already have a schedule assigned if using Entity parameter

    - The schedule ID must exist of the same type.  Different schedule types can have the same ID.  Schedule IDs can be found either on the attributes of climate devices or mode select entities or by looking at the schedule in the Wiser Schedule card.

    - The schedule being assigned must be of the correct type for the To Entity
        - climate to climate
        - smart plug to smart plug
        - light to light
        - shutter to shutter

    - If you have more than one hub, the schedule ID/'from' Entity' and To Entity must be from the same hub.

```
service: wiser.assign_schedule
data:
    entity_id: climate.wiser_kitchen
    to_entity_id: climate.wiser_lounge
```
```
service: wiser.assign_schedule
data:
    schedule_id: 5
    to_entity_id: climate.wiser_lounge
```



# Supported HA Built In Services

Many of the built in services for entity types are supported by this integration.  Below is a list of them.

### Climate Services
- All services related to setting HVAC mode, preset mode, target temperature etc.
- Entity target should be a wiser climate entity
- If using the set_preset_mode service the preset value should be the same as is listed in the preset dropdown on the climate card more info dialog.
    
    ```
    climate.set_hvac_mode
    climate.set_preset_mode
    climate.set_temperature
    climate.turn_on / climate.turn_off
    ```


### Switch Services
- All services related to turning a switch on or off.
- Entity target should be a wiser switch
    ```
    switch.turn_on
    switch.turn_off
    switch.toggle
    ```

### Select Services
- All services related to setting an option in any of the dropdown select lists for changing modes for hot water, smart plugs, lights and shutters (EU hubs only)
- Entity target should be a wiser select entity for mode
- The options for all mode selections are Manual or Auto
    ```
    select.select_option
    ```

### Button Services
- All services related to pushing a button to boost heating or hot water and cancel any overrides.
- Entity target should be a wiser button
    ```
    button.press
    ```

### Light Services (EU hub only)
- All services related to controlling a light (either dimmable or non dimmable)
- Entity target should be a wiser light
- Dimmable lights support the brightness parameter only.
    ```
    light.turn_on
    light.turn_off
    light.toggle
    ```

### Cover Services (EU hub only)
- All services related to controlling a blind type cover device
- Entity target should be a wiser cover
    ```
    cover.open_cover
    cover.close_cover
    cover.set_cover_position
    cover.stop_cover
    ```
