import mosaic
from mosaic.utilities.resource_path import resource_path

def GenerateTitle():
  return """
    <div flex layout="column" tabIndex="-1" role="main" class="md-whiteframe-z3">

      <md-toolbar ng-controller="AppCtrl" layout="row" hide-sm class="md-toolbar-tools md-toolbar-tools-center md-medium-tall md-whiteframe-z2">
        <a href="index.html" style="padding-top: 15px; padding-left: 25px;"><md-icon md-font-set="material-icons md-24">arrow_back</md-icon></img></a>
        <span flex></span>
        <md-button ng-href="{{docURL}}"><h4>Documentation</h4></md-button>
        <md-button ng-href="{{mailingListURL}}"><h4>Mailing List</h4></md-button>
        <md-button ng-href="https://github.com/usnistgov/mosaic"><h4>Develop</h4></md-button>
        <md-button ng-href="https://github.com/usnistgov/mosaic/issues"><h4>Issue Tracker</h4></md-button>
      </md-toolbar>

      <md-toolbar layout="row" hide-gt-sm class="md-whiteframe-z4" layout-align="center center">
        <md-button class="md-icon-button" aria-label="Settings" ng-click="toggleLeft()">
          <md-icon md-font-set="material-icons md-24">menu</md-icon>
        </md-button>

        <a href="index.html" style="text-decoration: none;"><h3><em>MOSAIC</em></h3></a>
        <span flex></span>
      </md-toolbar>

      <md-sidenav class="sidenav md-sidenav-left md-whiteframe-z2" md-component-id="left">
        <md-toolbar class="md-tall" style="background-color: #283593;">
          <span flex></span>
          <h1 class="md-toolbar-tools md-toolbar-tools-bottom">
            <span class="md-flex">MOSAIC</span>
          </h1>
        </md-toolbar>
        <md-content ng-controller="LeftCtrl" class="sidenav">
          <a href="{{docURL}}"><h2>Documentation</h2></a>
          <a href="{{mailingListURL}}"><h2>Mailing List</h2></a>
          <a href="https://github.com/usnistgov/mosaic"><h2>Develop</h2></a>
          <a href="https://github.com/usnistgov/mosaic/issues"><h2>Issue Tracker</h2></a>
        </md-content>
      </md-sidenav>

      <md-content flex id="content">
          <div layout="row" class="download-page" layout-align="center center">
            <div flex="10" flex-sm="20"><img src="assets/img/icon100px.png" width="50%"></img></div>
            <div flex><h2>Downloads</h2></div>
          </div>
  """

def GenerateHeader():
  return """
  <head>
    <title>MOSAIC Downloads</title>
    <link rel="icon" href="assets/img/favicon.ico" type="image/ico"/>

    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <meta http-equiv="Content-Language" content="en"/>
    <meta http-equiv="Content-Style-Type" content="text/css"/>
    <meta name="description" content="MOSAIC is a modular single-molecule analysis toolbox to decode multi-state nanopore data."/>
    <meta name="author" content="Arvind Balijepalli"/>
    <meta name="google-site-verification" content="BXETzCWmp_8xdMvDlUidbzJ4zbvyjVnNwiabBPnCvDk"/>
    <meta name="msvalidate.01" content="6486B1AC4BD85BB7125DD2B47CA4E4C5"/>

    <meta name="viewport" content="initial-scale=1, maximum-scale=1, user-scalable=no" />

    <link rel='stylesheet' href='https://fonts.googleapis.com/css?family=Roboto:200,300,400,400italic'>
    <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
    <link rel="stylesheet" href="https://ajax.googleapis.com/ajax/libs/angular_material/0.10.0/angular-material.min.css">

    <link rel="stylesheet" href="assets/app.css"/>

    <script type="text/javascript" id="_fed_an_js_tag" src="https://www.nist.gov/sites/default/files/js/federated-analytics.all.min.js?agency=NIST&subagency=github&pua=UA-42404149-54&yt=true&exts=ppsx,pps,f90,sch,rtf,wrl,txz,m1v,xlsm,msi,xsd,f,tif,eps,mpg,xml,pl,xlt,c">
    </script>
  </head>
  
  <body ng-app="mosaicApp" layout="row" ng-controller="AppCtrl">
  """
def GenerateTableFromVersion(baseurl, title, version, build, showBinaries=True):
  tabsrc="""
    <md-list>
            <md-subheader class="md-no-sticky"><h3>{0}</h3></md-subheader>
    """.format(title)
  if showBinaries:
    tabsrc+="""
      <md-list-item class="md-1-line">
              <div flex class="md-list-item-text download-links" layout="row">
                <div flex><a href="{0}/mosaic-{1}{2}.dmg"><h4>mosaic-v{1}{2}.dmg</h4></a></div>
                <div flex><h4>Mac OS X, 10.8+</h4></div>
              </div>
            </md-list-item>

            <md-list-item class="md-1-line">
              <div flex class="md-list-item-text download-links" layout="row">
                <div flex><a href="{0}/mosaic-x64-{1}{2}.zip"><h4>mosaic-x64-{1}{2}.zip</h4></a></div>
                <div flex><h4>Windows, 64-bit</h4></div>
              </div>
            </md-list-item>
    """.format(baseurl, version, build)
  tabsrc+="""
      <md-list-item class="md-1-line">
              <div flex class="md-list-item-text download-links" layout="row">
                <div flex><a href="{0}/mosaic-nist-{1}{2}.tar.gz"><h4>mosaic-nist-{1}{2}.tar.gz</h4></a></div>
                <div flex><h4>MOSAIC Source</h4></div>
              </div>
            </md-list-item>""".format(baseurl, version, build)
  if showBinaries:
    tabsrc+="""
            <md-list-item class="md-1-line">
              <div flex class="md-list-item-text download-links" layout="row">
                <div flex><a href="https://github.com/usnistgov/mosaic/releases/download/v1.0/MOSAICReferenceData.zip"><h4>mosaic-reference-data.zip</h4></a></div>
                <div flex><h4>MOSAIC Reference Data</h4></div>
              </div>
            </md-list-item>"""
  tabsrc+="""
      <md-divider ></md-divider>
        </md-list>
  """

  return tabsrc

if __name__ == '__main__':
  with open( resource_path('version-hash'), 'r' ) as f:
      version=f.read().strip()

  url="https://github.com/usnistgov/mosaic/releases/download/v"
  vers=[
    ("Version "+str(version), str(version), '.4932336', True),
    ("Version 1.3.2", "1.3.2", ".d88866c", False),
    ("Version 1.3.1", "1.3.1", ".9977009", False),
    ("Version 1.3", "1.3", ".f0e754c", False),
    ("Version 1.2", "1.2", "", False),
    ("Version 1.1", "1.1", "", False),
    ("Version 1.0", "1.0", "", False)
    ]
  htmlout="""
  <!DOCTYPE html>
  <html lang="en">
  """

  htmlout+=GenerateHeader()
  htmlout+=GenerateTitle()
  for v in vers:
    htmlout+=GenerateTableFromVersion(url+v[1], v[0], v[1], v[2])
  htmlout+="""
    </md-content>
    </div>
 
    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.3.15/angular.min.js"></script>
    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.3.15/angular-animate.min.js"></script>
    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.3.15/angular-aria.min.js"></script>
    <script src="https://ajax.googleapis.com/ajax/libs/angular_material/0.10.0/angular-material.min.js"></script>

    <script src="mosaic.js"></script>

  </body>
</html>"""

  with open('download.html', 'w') as f:
    f.write(htmlout)

  print "Wrote download.html"

