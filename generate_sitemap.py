#!/usr/bin/env python

"""
Generate sitemap.xml file for a Sphinx documentation.
This script is called after the sphinx build is completed.
(c) Mark Fink August 2010

Find documentation on sitemap.xml files:
http://www.google.com/support/webmasters/bin/topic.py?topic=8476
http://sitemaps.org/protocol.php

You can specify the location of the Sitemap using a robots.txt file. To do this, simply add the following line including the full URL to the

Sitemap: http://www.testing-software.org/sitemap.xml

Sample sitemap.xml file:
<?xml version='1.0' encoding='UTF-8'?>
<urlset xmlns='http://www.google.com/schemas/sitemap/0.84'>
<url>
<loc>http://www.testing-software.org</loc>
<lastmod>2010-08-05</lastmod>
<changefreq>weekly</changefreq>
<priority>0.5</priority>
</url>
<url>
...
"""

from os.path import isdir, join, abspath
import os
from glob import glob
import string
import time

ROOTWEB = 'https://usnistgov.github.io/mosaic'
WEBSITE = ROOTWEB + '/html'

# Document extentions we are interested in generating data for.
EXTENSIONS = ['.pdf', '.html']
EXCLUDE = ['source/doc/*']

SPHINX_SOURCE = './source/doc'
SPHINX_BUILD = './html'

# The default default is 'weekly'
DEFAULT_FREQ = 'weekly'
DEFAULT_PRIORITY = '0.5'

SITEMAP_FILENAME = 'sitemap.xml'


def process_directory(build_dir=SPHINX_BUILD, source_dir=SPHINX_SOURCE,
        base_dir = '', extensions=EXTENSIONS, frequency=DEFAULT_FREQ, 
        priority=DEFAULT_PRIORITY, website=WEBSITE, out=SITEMAP_FILENAME, 
        exclude = []):
    for fname in os.listdir(os.path.join(os.getcwd(), build_dir, base_dir)):
        full_path = abspath(join(os.getcwd(), build_dir, base_dir, fname))
        if full_path in exclude:
            # do not process source_dir (if within build_dir)
            pass
        elif isdir(full_path):
            process_directory(build_dir, source_dir, join(base_dir, fname),
                out=out, exclude=exclude)
        else:
            name, ext = os.path.splitext(fname)
        
            if ext in extensions:
                modtime = os.path.getmtime(full_path)
                if ext == '.html':
                    # for html extensions use the timestamp of the rst 
                    # souce-file whenever possible
                    try:
                        modtime = os.path.getmtime(join(os.getcwd(), source_dir,
                            base_dir, name + '.rst'))
                    except OSError:
                        pass
                if base_dir:
                    base_dir = base_dir.rstrip(os.sep) + os.sep
                iso_time = time.strftime('%Y-%m-%d', time.localtime(modtime))  
                url = website + '/' + base_dir.replace(os.sep, '/') + fname
               
                # add the information to sitemap.xml
                out.write('<url>\n')
                out.write('  <loc>' + url +'</loc>\n')
                out.write('  <lastmod>' + str(iso_time) + '</lastmod>\n')
                out.write('  <changefreq>' + frequency + '</changefreq>\n')
                out.write('  <priority>' + priority + '</priority>\n')
                out.write('</url>\n')

root_url="""<url>
  <loc>{url}</loc>
  <lastmod>{modtime}</lastmod>
  <changefreq>weekly</changefreq>
  <priority>1.0</priority>
</url>
"""

def main():
    """Write header and footer of the sitemap.xml file and start
    processing of the sphinx build results.
    """

    exclude = sum([glob(x) for x in EXCLUDE], [])
    full_exclude = [join(os.getcwd(), f) for f in exclude]
    root_pages=['index.offline.html', 'platforms.html']

    out = open(os.getcwd() + os.sep + SITEMAP_FILENAME, 'w')

    out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    out.write('<urlset xmlns="http://www.google.com/schemas/sitemap/0.9">\n')

    for page in root_pages:
        out.write( root_url.format(url=ROOTWEB+'/'+page,modtime=time.strftime('%Y-%m-%d', time.localtime(os.path.getmtime(os.getcwd()+'/'+page)))) )

    docweb=WEBSITE+'/html'
    process_directory(out=out, exclude=full_exclude)

    out.write('</urlset>\n')
    
    out.close()

    robots = open(os.getcwd() + os.sep + 'robots.txt', 'w')
    robots.write('Sitemap: '+ WEBSITE +'/sitemap.xml')
    robots.close()

if __name__ == '__main__':
    main()

