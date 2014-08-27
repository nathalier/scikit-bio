# ----------------------------------------------------------------------------
# Copyright (c) 2013--, scikit-bio development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

from __future__ import absolute_import, division, print_function
from future.utils.six import StringIO

from unittest import TestCase, main

import numpy as np
import numpy.testing as npt

from skbio.io import OrdResFormatError
from skbio.io.ordres import (_ordres_to_ordination_results,
                             _ordination_results_to_ordres, _ordres_sniffer)
from skbio.stats.ordination import OrdinationResults
from skbio.util import get_data_path


class OrdResTestData(TestCase):
    def setUp(self):
        self.valid_fps = map(
            get_data_path,
            ['ordres_L&L_CA_data_scores', 'ordres_example3_scores',
             'ordres_PCoA_sample_data_3_scores', 'ordres_example2_scores'])

        self.invalid_fps = map(lambda e: (get_data_path(e[0]), e[1]), [
            ('ordres_error1', 'Eigvals header'),
            ('ordres_error2', 'Proportion explained header'),
            ('ordres_error3', 'Species header'),
            ('ordres_error4', 'Site header'),
            ('ordres_error5', 'Biplot header'),
            ('ordres_error6', 'Site constraints header'),
            ('ordres_error7', 'empty line'),
            ('ordres_error8', '9 proportion explained.*8'),
            ('ordres_error9', '2 values.*1 in row 1'),
            ('ordres_error10', '2 values.*1 in row 1'),
            ('ordres_error11', 'Site constraints ids and site ids'),
            ('ordres_error12', '9 eigvals.*8'),
            ('ordres_error13', '9 proportion explained.*8'),
            ('ordres_error14', 'Site is 0: 9 x 0'),
            ('ordres_error15', '9 values.*8 in row 1'),
            ('ordres_error16', 'Biplot is 0: 3 x 0'),
            ('ordres_error17', '3 values.*2 in row 1'),
            ('ordres_error18', 'proportion explained.*eigvals: 8 != 9'),
            ('ordres_error19', 'coordinates per species.*eigvals: 1 != 2'),
            ('ordres_error20', 'coordinates per site.*eigvals: 1 != 2'),
            ('ordres_error21', 'one eigval')
        ])


class OrdinationResultsReaderWriterTests(OrdResTestData):
    def setUp(self):
        super(OrdinationResultsReaderWriterTests, self).setUp()

        # define in-memory results, one for each of the valid files in
        # self.valid_fps

        # CA results
        eigvals = np.array([0.0961330159181, 0.0409418140138])
        species = np.array([[0.408869425742, 0.0695518116298],
                            [-0.1153860437, -0.299767683538],
                            [-0.309967102571, 0.187391917117]])
        site = np.array([[-0.848956053187, 0.882764759014],
                         [-0.220458650578, -1.34482000302],
                         [1.66697179591, 0.470324389808]])
        biplot = None
        site_constraints = None
        prop_explained = None
        species_ids = ['Species1', 'Species2', 'Species3']
        site_ids = ['Site1', 'Site2', 'Site3']
        ca_scores = OrdinationResults(eigvals=eigvals, species=species,
                                      site=site, biplot=biplot,
                                      site_constraints=site_constraints,
                                      proportion_explained=prop_explained,
                                      species_ids=species_ids,
                                      site_ids=site_ids)
        # CCA results
        eigvals = np.array([0.366135830393, 0.186887643052, 0.0788466514249,
                            0.082287840501, 0.0351348475787, 0.0233265839374,
                            0.0099048981912, 0.00122461669234,
                            0.000417454724117])
        species = np.loadtxt(get_data_path('ordres_exp_OrdRes_CCA_species'))
        site = np.loadtxt(get_data_path('ordres_exp_OrdRes_CCA_site'))
        biplot = np.array([[-0.169746767979, 0.63069090084, 0.760769036049],
                           [-0.994016563505, 0.0609533148724,
                            -0.0449369418179],
                           [0.184352565909, -0.974867543612, 0.0309865007541]])
        site_constraints = np.loadtxt(
            get_data_path('ordres_exp_OrdRes_CCA_site_constraints'))
        prop_explained = None
        species_ids = ['Species0', 'Species1', 'Species2', 'Species3',
                       'Species4', 'Species5', 'Species6', 'Species7',
                       'Species8']
        site_ids = ['Site0', 'Site1', 'Site2', 'Site3', 'Site4', 'Site5',
                    'Site6', 'Site7', 'Site8', 'Site9']
        cca_scores = OrdinationResults(eigvals=eigvals, species=species,
                                       site=site, biplot=biplot,
                                       site_constraints=site_constraints,
                                       proportion_explained=prop_explained,
                                       species_ids=species_ids,
                                       site_ids=site_ids)
        # PCoA results
        eigvals = np.array([0.512367260461, 0.300719094427, 0.267912066004,
                            0.208988681078, 0.19169895326, 0.16054234528,
                            0.15017695712, 0.122457748167, 0.0])
        species = None
        site = np.loadtxt(get_data_path('ordres_exp_OrdRes_PCoA_site'))
        biplot = None
        site_constraints = None
        prop_explained = np.array([0.267573832777, 0.15704469605,
                                   0.139911863774, 0.109140272454,
                                   0.100111048503, 0.0838401161912,
                                   0.0784269939011, 0.0639511763509, 0.0])
        species_ids = None
        site_ids = ['PC.636', 'PC.635', 'PC.356', 'PC.481', 'PC.354', 'PC.593',
                    'PC.355', 'PC.607', 'PC.634']
        pcoa_scores = OrdinationResults(eigvals=eigvals, species=species,
                                        site=site, biplot=biplot,
                                        site_constraints=site_constraints,
                                        proportion_explained=prop_explained,
                                        species_ids=species_ids,
                                        site_ids=site_ids)
        # RDA results
        eigvals = np.array([25.8979540892, 14.9825779819, 8.93784077262,
                            6.13995623072, 1.68070536498, 0.57735026919,
                            0.275983624351])
        species = np.loadtxt(get_data_path('ordres_exp_OrdRes_RDA_species'))
        site = np.loadtxt(get_data_path('ordres_exp_OrdRes_RDA_site'))
        biplot = np.array([[0.422650019179, -0.559142585857, -0.713250678211],
                           [0.988495963777, 0.150787422017, -0.0117848614073],
                           [-0.556516618887, 0.817599992718, 0.147714267459],
                           [-0.404079676685, -0.9058434809, -0.127150316558]])
        site_constraints = np.loadtxt(
            get_data_path('ordres_exp_OrdRes_RDA_site_constraints'))
        prop_explained = None
        species_ids = ['Species0', 'Species1', 'Species2', 'Species3',
                       'Species4', 'Species5']
        site_ids = ['Site0', 'Site1', 'Site2', 'Site3', 'Site4', 'Site5',
                    'Site6', 'Site7', 'Site8', 'Site9']
        rda_scores = OrdinationResults(eigvals=eigvals, species=species,
                                       site=site, biplot=biplot,
                                       site_constraints=site_constraints,
                                       proportion_explained=prop_explained,
                                       species_ids=species_ids,
                                       site_ids=site_ids)

        self.ordination_results_objs = [ca_scores, cca_scores, pcoa_scores,
                                        rda_scores]

    def check_ordination_results_equal(self, obs, exp):
        npt.assert_almost_equal(obs.eigvals, exp.eigvals)
        if exp.species is not None:
            npt.assert_almost_equal(obs.species, exp.species)
        else:
            npt.assert_equal(obs.species, exp.species)
        npt.assert_equal(obs.species_ids, exp.species_ids)

        if exp.site is not None:
            npt.assert_almost_equal(obs.site, exp.site)
        else:
            npt.assert_equal(obs.site, exp.site)
        npt.assert_equal(obs.site_ids, exp.site_ids)

        if exp.biplot is not None:
            npt.assert_almost_equal(obs.biplot, exp.biplot)
        else:
            npt.assert_equal(obs.biplot, exp.biplot)

        if exp.site_constraints is not None:
            npt.assert_almost_equal(obs.site_constraints, exp.site_constraints)
        else:
            npt.assert_equal(obs.site_constraints, exp.site_constraints)

        if exp.proportion_explained is not None:
            npt.assert_almost_equal(obs.proportion_explained,
                                    exp.proportion_explained)
        else:
            npt.assert_equal(obs.proportion_explained,
                             exp.proportion_explained)

    def test_read_valid_files(self):
        for fp, obj in zip(self.valid_fps, self.ordination_results_objs):
                obs = _ordres_to_ordination_results(fp)
                self.check_ordination_results_equal(obs, obj)

    def test_read_invalid_files(self):
        for invalid_fp, error_msg_regexp  in self.invalid_fps:
            with self.assertRaisesRegexp(OrdResFormatError, error_msg_regexp):
                _ordres_to_ordination_results(invalid_fp)

    def test_write(self):
        for fp, obj in zip(self.valid_fps, self.ordination_results_objs):
            fh = StringIO()
            _ordination_results_to_ordres(obj, fh)
            obs = fh.getvalue()
            fh.close()

            with open(fp, 'U') as fh:
                exp = fh.read()

            npt.assert_equal(obs, exp)

    def test_roundtrip_read_write(self):
        for fp in self.valid_fps:
            # Read.
            obj1 = _ordres_to_ordination_results(fp)

            # Write.
            fh = StringIO()
            _ordination_results_to_ordres(obj1, fh)
            fh.seek(0)

            # Read.
            obj2 = _ordres_to_ordination_results(fh)
            fh.close()

            self.check_ordination_results_equal(obj1, obj2)


if __name__ == '__main__':
    main()
