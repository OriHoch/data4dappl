from datapackage_pipelines_ckan.processors.dump.to_ckan import CkanDumper
import logging


class FoiOfficesCkanDumper(CkanDumper):

    def prepare_datapackage(self, datapackage, params):
        hashes = {r['name']: r.get('hash') for r in datapackage['resources']}
        self.__needs_update = hashes.get('old_foi_offices') != hashes['foi_offices']
        resource_names = [r['name'] for r in datapackage['resources']]
        self.__new_resource_idx = resource_names.index('foi_offices')
        if self.__needs_update:
            datapackage['resources'] = [r for r in datapackage['resources'] if r['name'] == 'foi_offices']
        else:
            datapackage['resources'] = []
        return super(FoiOfficesCkanDumper, self).prepare_datapackage(datapackage, params)

    def handle_resources(self, datapackage, resource_iterator, parameters, stats):
        if self.__needs_update:
            def get_resources():
                for idx, r in enumerate(resource_iterator):
                    if idx == self.__new_resource_idx:
                        yield r
                    else:
                        for row in r:
                            pass
            yield from super(FoiOfficesCkanDumper, self).handle_resources(datapackage, get_resources(), parameters, stats)
        else:
            for r in resource_iterator:
                for row in r:
                    pass


if __name__ == '__main__':
    FoiOfficesCkanDumper()()
