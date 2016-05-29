import nose

def _mosaicUnitTests(base):
    class mosaicUnitTests(base):
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
                    testList.extend(['adept_Test', 'cusum_Test', 'adept2State_Test'])
                if self.segment:
                    testList.extend(['eventPartition_Test', 'eventPartitionParallel_Test'])
                if self.dependencies:
                    testList.extend(['dependencyVersion_Test'])
                if self.modules:
                    testList.extend(['import_Tests'])

                if self.verbose:
                    testargs=['mosaic', '-v', '--where=mosaic/utest/']
                else:
                    testargs=['mosaic', '--where=mosaic/utest/']
                
                testargs.extend(testList)

                return nose.main(argv=testargs)
            except:
                raise

    return mosaicUnitTests