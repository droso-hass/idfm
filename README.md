# Ile de france mobilités integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

Allows to retreive next schedules for a stations on a specific line and traffic informations for a line. Metro, RER, Transilien, Tram and BUS are supported.

Based on the [PRIM API](https://prim.iledefrance-mobilites.fr) and the python library [idfm-api](https://github.com/droso-hass/idfm-api).

## Note on line/stop selection

The lines and stops listings are now fetched at the first run of the configuration process (and re-fetched if you restart home-assistant), this will take a few seconds. This means that the datasets are now more up-to-date, which also means that they are subject to changes: some lines/stops might disappear if the traffic is interrupted/replaced by bus, especially for train lines.

**Before opening an issue**, please ensure that you can find your line (with the correct TransportMode) [here](https://data.iledefrance-mobilites.fr/explore/dataset/referentiel-des-lignes/table) (note the ID_Line field) and that there are stops corresponding to this ID_Line (paste it in the search field) [here](https://data.iledefrance-mobilites.fr/explore/dataset/arrets-lignes/table).

## Configuration

In order to use this integration, you need to create an account on the [PRIM website](https://prim.iledefrance-mobilites.fr) and get your API token [here](https://prim.iledefrance-mobilites.fr/fr/mon-jeton-api).

By default, each instance of the integration will generate 2 requests every 3 min (except between 1h30 and 5h30).

The limitations are set to:
 - 1 000 000 requests per day for the [next schedules api](https://prim.iledefrance-mobilites.fr/fr/donnees-dynamiques/idfm-ivtr-requete_unitaire?type=k)
 - 20 000 requests per day for the [info traffic api](https://prim.iledefrance-mobilites.fr/fr/donnees-dynamiques/idfm-ivtr-info_trafic?type=k&apiId=idfm-ivtr-info_trafic).

So with the default settings you generate about 400 calls per day, thus you are limited to a maximum of 50 instances.

## Manually Updating

If the default interval is not ok for you, you can decide to manually trigger the updates of the entities:

Go in Settings > Integrations then on the IDFM integration click on the three-dots button and select "System Options". You can now click on "Enable polling for updates." to disable the auto updating (note that you will need to restart Home Assistant for the changes to take effect).

You can now use the [homeassistant.update_entity](https://www.home-assistant.io/integrations/homeassistant/#service-homeassistantupdate_entity) service to manually update the entities (see the example below), you only need to reference one entity to refresh all the entities of the same instance.

You can also use the examples of the [maps travel time integration](https://www.home-assistant.io/integrations/google_travel_time/#updating-sensors-on-demand-using-automation) as a source of inspiration.

```yaml
service: homeassistant.update_entity
target:
  entity_id: sensor.idfm_gare_de_lyon_paris_chateau_de_vincennes_0
```