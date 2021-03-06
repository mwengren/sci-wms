# -*- coding: utf-8 -*-
import unittest
from copy import copy

from django.test import TestCase
from wms.tests import add_server, add_group, add_user, add_dataset, image_path
from wms.models import Dataset, RGridDataset

import pytest
xfail = pytest.mark.xfail


@xfail(reason="RGRID Datasets are not implemented yet")
class TestRgrid(TestCase):

    @classmethod
    def setUpClass(cls):
        add_server()
        add_group()
        add_user()
        add_dataset("rgrid_testing", "rgrid", "satellite_rgrid.nc")

    @classmethod
    def tearDownClass(cls):
        d = Dataset.objects.get(slug="rgrid_testing")
        d.delete()

    def setUp(self):
        self.dataset_slug = 'rgrid_testing'
        self.url_params = dict(
            service     = 'WMS',
            request     = 'GetMap',
            version     = '1.1.1',
            layers      = 'sst',
            format      = 'image/png',
            transparent = 'true',
            height      = 256,
            width       = 256,
            srs         = 'EPSG:3857',
            bbox        = '-9079495.967826376,5165920.119625353,-8922952.933898335,5322463.153553393'
        )

    def image_name(self):
        return '{}.png'.format(self.id().split('.')[-1])

    def test_identify(self):
        d = Dataset.objects.get(name=self.dataset_slug)
        klass = Dataset.identify(d.uri)
        assert klass == RGridDataset

    def do_test(self, params, write=True):
        response = self.client.get('/wms/datasets/{}'.format(self.dataset_slug), params)
        self.assertEqual(response.status_code, 200)
        if write is True:
            with open(image_path(self.__class__.__name__, self.image_name()), "wb") as f:
                f.write(response.content)

    def test_filledcontours(self):
        params = copy(self.url_params)
        params.update(styles='filledcontours_cubehelix')
        self.do_test(params)

    def test_facets(self):
        params = copy(self.url_params)
        params.update(styles='facets_cubehelix')
        self.do_test(params)

    def test_pcolor(self):
        params = copy(self.url_params)
        params.update(styles='pcolor_cubehelix')
        self.do_test(params)

    def test_contours(self):
        params = copy(self.url_params)
        params.update(styles='contours_cubehelix')
        self.do_test(params)

    def test_getCaps(self):
        params = dict(request='GetCapabilities')
        self.do_test(params, write=False)

    def test_create_layers(self):
        d = Dataset.objects.get(slug=self.dataset_slug)
        assert d.layer_set.count() == 1

    def test_delete_cache_signal(self):
        d = add_dataset("rgrid_deleting", "rgrid", "satellite_rgrid.nc")
        self.assertTrue(d.has_cache())
        d.clear_cache()
        self.assertFalse(d.has_cache())
