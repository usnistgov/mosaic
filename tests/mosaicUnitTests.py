import mosaic.utilities.mosaicLogging as mlog 
import nose

def _mosaicUnitTests(base):
    class mosaicUnitTests(base):
        log=mlog.mosaicLogging().getLogger(__name__)

        description = "run the MOSAIC unit test suite."
        user_options = [
                        ('algorithms','a', 'run algorithmic tests'),
                        ('apps','p', 'run top-level application tests'),
                        ('segment','s', 'run time-series segmentation tests'),
                        ('dependencies', 'd', 'test MOSAIC dependency versions'),
                        ('modules', 'm', 'test MOSAIC modules'),
                        ('trajio', 't', 'test MOSAIC I/O'),
                        ('mdio', 'i', 'test MOSAIC MDIO'),
                        ('mosaicweb', 'w', 'test MOSAIC web')
                        ]

        def initialize_options(self):
            self.algorithms=0
            self.apps=0
            self.segment=0
            self.dependencies=0
            self.modules=0
            self.trajio=0
            self.mdio=0
            self.mosaicweb=0

        def finalize_options(self):
            pass

        def run(self):
            try:
                testList=[]
                testargs=['mosaic']

                if self.algorithms:
                    mosaicUnitTests.log.debug("Running algorithm unit tests")
                    testList.extend(['mosaic/tests/adept2State_Test.py', 'mosaic/tests/adept_Test.py', 'mosaic/tests/cusum_Test.py'])
                if self.apps:
                    mosaicUnitTests.log.debug("Running top-level applications unit tests")
                    testList.extend(['mosaic/tests/apps_Test.py'])
                if self.segment:
                    mosaicUnitTests.log.debug("Running event segmentation unit tests")
                    testList.extend(['mosaic/tests/eventPartition_Test.py', 'mosaic/tests/eventPartitionParallel_Test.py'])
                if self.dependencies:
                    mosaicUnitTests.log.debug("Running dependency unit tests")
                    testList.extend(['tests/dependencyVersion_Test.py'])
                if self.modules:
                    mosaicUnitTests.log.debug("Running module import unit tests")
                    testList.extend(['mosaic/tests/import_Tests.py'])
                if self.trajio:
                    mosaicUnitTests.log.debug("Running module trajectory I/O unit tests")
                    testList.extend(['mosaic/tests/trajio_Test.py'])
                if self.mdio:
                    mosaicUnitTests.log.debug("Running module metadata I/O unit tests")
                    testList.extend(['mosaic/tests/mdio_Test.py'])                  
                if self.mosaicweb:
                    mosaicUnitTests.log.debug("Running module Mosaic web unit tests")
                    testList.extend(['mosaicweb/tests/status_Test.py', 'mosaicweb/tests/session_Test.py'])

                if self.verbose:
                    mosaicUnitTests.log.debug("Running verbose unit tests")
                    testargs.extend(['-v'])
                else:
                    testargs.extend([])
                
                testargs.extend(testList)

                return nose.run(argv=testargs)
            except:
                raise

    return mosaicUnitTests