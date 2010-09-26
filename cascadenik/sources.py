import ConfigParser
import StringIO

class DataSources(object):
    def __init__(self):
        self.bases = set([])
        self.parser = None
        self.sources = {}

    def add_config(self, textdata, filename):
        data = StringIO.StringIO(textdata)
        data.seek(0)
        if self.parser:
            self.parser = ChainedConfigParser(self.parser)
        else:
            self.parser = ConfigParser.SafeConfigParser()
        self.parser.readfp(data)

        for sect in self.parser.sections():
            options = {}
            name = sect
            dtype = self.parser.get(sect,"type") if self.parser.has_option(sect, "type") else None
            base = self.parser.get(sect,"base") if self.parser.has_option(sect, "base") else None
            layer_srs = self.parser.get(sect,"layer_srs") if self.parser.has_option(sect, "layer_srs") else None


            # this layer declares a base
            if base:
                self.bases.add(base)
                # the base may have been declared already, or we haven't processed it yet.
                if base in self.sources:
                    dtype = self.sources[base]['parameters']["type"]
                else:
                    dtype = self.parser.get(base,"type")
                    
            if dtype:
                options['type'] = dtype
            else:
                raise Exception("Section [%s] missing 'type' information in %s." % (sect, filename))
            
            # now populate the options for this type of source, looping over all the valid params
            for option, option_type in self.XML_OPTIONS[dtype].items():
                opt_value = None
                try:
                    if option_type == int:
                        opt_value = self.parser.getint(sect,option)
                    elif option_type == float:
                        opt_value = self.parser.getfloat(sect,option)
                    elif option_type == bool:
                        opt_value = self.parser.getboolean(sect,option)
                    else:
                        opt_value = self.parser.get(sect,option)
                except ConfigParser.NoOptionError:
                    pass

                if opt_value is not None:
                    options[option] = opt_value

            # build an object mirroring the XML Datasource object
            conf = dict(parameters=options)
            if base:
                conf['base'] = base
            if layer_srs:
                conf['layer_srs'] = layer_srs
            self.sources[name] = conf
                

    XML_OPTIONS = {"shape" : dict(file=str,encoding=str),
                   "postgis" : dict(cursor_size=int,
                                    dbname=str,
                                    geometry_field=str,
                                    extent=str,
                                    estimate_extent=bool,
                                    host=str,
                                    initial_size=int,
                                    max_size=int,
                                    multiple_geometries=bool,
                                    password=str,
                                    persist_connection=bool,
                                    port=int,
                                    row_limit=int,
                                    table=str,
                                    srid=str,
                                    user=str),
                   "ogr" : dict(layer=str),
                   "osm" : dict(file=str, parser=str, url=str, bbox=str),
                   "global": dict(type=str, estimate_extent=bool, extent=str)               
                   }

class ChainedConfigParser(ConfigParser.SafeConfigParser):
    def __init__(self, last):
        ConfigParser.SafeConfigParser.__init__(self)
        d = last.defaults()
        d.update(self._defaults)
        self._defaults = d 

