import mosaic.utilities.mosaicLogging as mlog 
import nose

def _mosaicUnitTests(base):
    class mosaicUnitTests(base):
        log=mlog.mosaicLogging().getLogger(__name__)

        description = "run the MOSAIC unit test suite."
        user_options = [
                        ('algorithms','a', 'run algorithmic tests'),
                        ('segment','s', 'run time-series segmentation tests'),
                        ('dependencies', 'd', 'test MOSAIC dependency versions'),
                        ('modules', 'm', 'test MOSAIC modules')
                        ]

        def initialize_options(self):
            self.algorithms=0
            self.segment=0
            self.dependencies=0
            self.modules=0

        def finalize_options(self):
            pass

        def run(self):
            try:
                testList=[]

                if self.algorithms:
                    mosaicUnitTests.log.debug("Running algorithm unit tests")
                    testList.extend(['adept_Test', 'cusum_Test', 'adept2State_Test'])
                if self.segment:
                    mosaicUnitTests.log.debug("Running event segmentation unit tests")
                    testList.extend(['eventPartition_Test', 'eventPartitionParallel_Test'])
                if self.dependencies:
                    mosaicUnitTests.log.debug("Running dependency unit tests")
                    testList.extend(['dependencyVersion_Test'])
                if self.modules:
                    mosaicUnitTests.log.debug("Running module import unit tests")
                    testList.extend(['import_Tests'])

                if self.verbose:
                    mosaicUnitTests.log.debug("Running verbose unit tests")
                    testargs=['mosaic', '-v', '--where=mosaic/utest/']
                else:
                    testargs=['mosaic', '--where=mosaic/utest/']
                
                testargs.extend(testList)

                return nose.main(argv=testargs)
            except:
                raise

    return mosaicUnitTests