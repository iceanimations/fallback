# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 30 2018, 16:30:26) [MSC v.1500 64 bit (AMD64)]
# Embedded file name: C:/Users/qurban.ali.ICE-144/Documents/maya/scripts\shot_subm\__init__.py
# Compiled at: 2017-11-08 17:37:11
import src._submit as subm
reload(subm)
Window = subm.Submitter
import pymel.core as pc
doCreateGeometryCache2 = 'global proc string[] doCreateGeometryCache2 ( int $version, string $args[] )\n//A facsimle copy of doCreateGeometryCache just that args[6] i.e. export cache\n//per geometry is fixed to 1 regardless of group caching\n{\n        string $cacheFiles[];\n        if(( $version > 5 ) || ( size($args) > 16 )) {\n                error( (uiRes("m_doCreateGeometryCache.kBadArgsError")));\n                return $cacheFiles;\n        }\n\n        string  $cacheDirectory         = "";\n        string  $fileName                       = "";\n        int             $useAsPrefix            = 0;\n        int             $perGeometry            = 0;\n        string  $action        = "replace";\n        int     $force = 0;\n        int             $inherit = 0;\n        int     $doubleToFloat = 0;\n        string $distribution = "OneFilePerFrame";\n\n        int     $rangeMode                      = $args[0];\n        float   $diskCacheStartTime = $args[1];\n        float   $diskCacheEndTime   = $args[2];\n        float   $simulationRate         = 1.0;\n        int             $sampleMultiplier       = 1;\n\n        float  $startTime = $diskCacheStartTime;\n        float  $endTime = $diskCacheEndTime;\n        string $format = "mcc";         // Maya\'s default internal format\n\n        if( $rangeMode == 1 ) {\n        $startTime = `getAttr defaultRenderGlobals.startFrame`;\n        $endTime = `getAttr defaultRenderGlobals.endFrame`;\n        } else if( $rangeMode == 2 ) {\n                $startTime = `playbackOptions -q -min`;\n                $endTime = `playbackOptions -q -max`;\n        }\n\n        if ($version > 1) {\n            $distribution = $args[3];\n                $cacheDirectory = $args[5];\n                $perGeometry = $args[6];\n                $fileName = $args[7];\n                $useAsPrefix = $args[8];\n        }\n        if ($version > 2) {\n                $action = $args[9];\n                $force = $args[10];\n\n                if( size($args) > 11 ) {\n                        $simulationRate = $args[11];\n                }\n                if( size($args) > 12 ) {\n                        $sampleMultiplier = $args[12];\n                }\n                else {\n                        $sampleMultiplier = 1;\n                }\n        }\n        if( $version > 3 ) {\n                $inherit = $args[13];\n                $doubleToFloat = $args[14];\n        }\n\n        if( $version > 4 ) {\n                $format = $args[15];\n        }\n\n        // Call doMergeCache instead since it handles gaps between\n        // caches correctly.\n        if( $action == "merge" || $action == "mergeDelete" )\n        {\n\n                string $mergeArgs[];\n                $mergeArgs[0] = 1;\n                $mergeArgs[1] = $startTime;\n                $mergeArgs[2] = $endTime;\n                $mergeArgs[3] = $args[3];\n                $mergeArgs[4] = $cacheDirectory;\n                $mergeArgs[5] = $fileName;\n                $mergeArgs[6] = $useAsPrefix;\n                $mergeArgs[7] = $force;\n                $mergeArgs[8] = $simulationRate;\n                $mergeArgs[9] = $sampleMultiplier;\n                $mergeArgs[10] = $action;\n                $mergeArgs[11] = "geom";\n                $mergeArgs[12] = $format;\n                return doMergeCache(2, $mergeArgs);\n        }\n\n        // If we\'re replacing a cache, and inheriting modifications,\n        // the new cache should have the same translation, scaling\n        // and clipping as the original. So store these values and\n        // set after cache creation.\n        //\n        float $startFrame[] = {};\n        float $sourceStart[] = {};\n        float $sourceEnd[] = {};\n        float $scale[] = {};\n\n        select -d `ls -sl -type cacheFile`;\n        string $objsToCache[] = getGeometriesToCache();\n        if (size($objsToCache) == 0) {\n                error((uiRes("m_doCreateGeometryCache.kMustSelectGeom")));\n        } else  if ($action == "replace") {\n                if (!getCacheCanBeReplaced($objsToCache)) {\n                        return $cacheFiles;\n                }\n\n                if( $inherit ) {\n                        string $obj, $cache;\n                        for( $obj in $objsToCache ) {\n                                string $existing[] = findExistingCaches($obj);\n                                int $index = size($startFrame);\n                                $startFrame[$index] = `getAttr ($existing[0]+".startFrame")`;\n                                $sourceStart[$index] = `getAttr ($existing[0]+".sourceStart")`;\n                                $sourceEnd[$index] = `getAttr ($existing[0]+".sourceEnd")`;\n                                $scale[$index] = `getAttr ($existing[0]+".scale")`;\n                        }\n                }\n        }\n\n        // If the user has existing cache groups on some of the geometry,\n        // then they cannot attach new caches per geometry.\n        //\n    string $cacheGroups[] = `getObjectsByCacheGroup($objsToCache)`;\n        if (size($cacheGroups) != size($objsToCache)) {\n                $perGeometry = 1;\n                $args[6] = 1; // used below in generating cache file command\n                //warning( (uiRes("m_doCreateGeometryCache.kIgnoringPerGeometry")) );\n        }\n\n        // Check if directory has caches that might be overwritten\n        //\n        string $cacheDirectory = getCacheDirectory(     $cacheDirectory, "fileCache",\n                                                                                                $objsToCache, $fileName,\n                                                                                                $useAsPrefix, $perGeometry,\n                                                                                                $action, $force, 1);\n\n        if ($cacheDirectory == "") {\n                return $cacheFiles;\n        }\n        else if ($cacheDirectory == "rename") {\n                performCreateGeometryCache 1 $action;\n                error((uiRes("m_doCreateGeometryCache.kNameAlreadyInUse")));\n                return $cacheFiles;\n        }\n\n        // if we\'re replacing, delete active caches.\n        //\n        if( $action == "replace" ) {\n                for( $obj in $objsToCache ) {\n                        string $all[] = findExistingCaches($obj);\n                        for( $cache in $all) {\n                                if( `getAttr ($cache+".enable")`) {\n                                        deleteCacheFile(2, {"keep",$cache});\n                                }\n                        }\n                }\n        }\n\n        // create the cache(s)\n        //\n        if ($action == "add" || $action == "replace") {\n                setCacheEnable(0, 1, $objsToCache);\n        }\n\n        // generate the cacheFile command to write the caches\n        //\n        string $cacheCmd = getCacheFileCmd($version, $cacheDirectory, $args);\n        int $ii = 0;\n\n        //segmented cache files are employed in the case of one large cache file that\n        //exceeds 2GB in size.  Since we currently cannot handle such large files, we will\n        //automatically generate several caches, each less than 2GB.\n        int $useSegmentedCacheFile = 0;\n        int $numSegments = 0;\n        if($distribution == "OneFile" && !$perGeometry) {\n            string $queryCacheSizeCmd = "cacheFile";\n            for ($ii = 0; $ii < size($objsToCache); $ii++) {\n                    $queryCacheSizeCmd += (" -points "+$objsToCache[$ii]);\n            }\n            $queryCacheSizeCmd += " -q -dataSize";\n            if($doubleToFloat) {\n                $queryCacheSizeCmd += " -dtf";\n            }\n            float $dataSizePerFrame = `eval $queryCacheSizeCmd`;\n            float $maxSize = 2147000000; //approximate size of max signed int.\n            float $numSamples = ($endTime - $startTime + 1.0)/($simulationRate*$sampleMultiplier);\n            float $dataSize = $dataSizePerFrame*$numSamples;\n            if($dataSize > $maxSize) {\n                $useSegmentedCacheFile = 1;\n                $numSegments = floor($dataSize / $maxSize) + 1;\n            }\n        }\n\n        if(!$useSegmentedCacheFile) {\n            if( $fileName != "" ) {\n                    $cacheCmd += ("-fileName \\"" + $fileName + "\\" ");\n            }\n            $cacheCmd += ("-st "+$startTime+" -et "+$endTime);\n            for ($ii = 0; $ii < size($objsToCache); $ii++) {\n                    $cacheCmd += (" -points "+$objsToCache[$ii]);\n            }\n            $cacheFiles = `eval $cacheCmd`;\n        }\n        else {\n            int $jj;\n            float $segmentStartTime = $startTime;\n            float $segmentEndTime;\n            float $segmentLength = ($endTime - $startTime)/$numSegments;\n            string $segmentCacheCmd ;\n            string $segmentCacheName = "";\n            string $segmentCacheFiles[];\n            for($jj = 0; $jj< $numSegments; $jj++) {\n                $segmentCacheCmd = $cacheCmd;\n                if($fileName != "")\n                    $segmentCacheName = $fileName;\n                else\n                    $segmentCacheName = getAutomaticCacheName();\n                $segmentEndTime = $segmentStartTime + floor($segmentLength);\n\n                $segmentCacheName += ("Segment" + ($jj+1));\n                $segmentCacheCmd += (" -fileName \\"" + $segmentCacheName + "\\" ");\n\n                $segmentCacheCmd += ("-st "+$segmentStartTime+" -et "+$segmentEndTime);\n                for ($ii = 0; $ii < size($objsToCache); $ii++) {\n                        $segmentCacheCmd += (" -points "+$objsToCache[$ii]);\n                }\n                $segmentCacheFiles = `eval $segmentCacheCmd`;\n                $segmentStartTime = $segmentEndTime + 1;\n\n                $cacheFiles[size($cacheFiles)] = $segmentCacheFiles[0];\n            }\n    }\n\n        if ($action == "export") {\n                for ($ii = 0; $ii < size($cacheFiles); $ii++) {\n                        $cacheFiles[$ii] = ($cacheDirectory+"/"+$cacheFiles[$ii]+".xml");\n                }\n                // In export mode, we do not want to attach the cache. We are done.\n                //\n                return $cacheFiles;\n        }\n\n\n        // attach the caches to the history switch\n        //\n        if($useSegmentedCacheFile) {\n            if(size($objsToCache) == 1) {\n                for($ii=0;$ii<size($cacheFiles);$ii++) {\n                    string $segmentCacheFile[];\n                    $segmentCacheFile[0] = $cacheFiles[$ii];\n                    attachOneCachePerGeometry(  $segmentCacheFile, $objsToCache,\n                                                                        $cacheDirectory, $action, $format );\n                }\n            }\n            else {\n                for($ii=0;$ii<size($cacheFiles);$ii++) {\n                    string $segmentCacheFile[];\n                    $segmentCacheFile[0] = $cacheFiles[$ii];\n                    attachCacheGroups( $segmentCacheFile,$objsToCache,$cacheDirectory,$action, $format );\n                }\n            }\n\n        }\n        else if( $perGeometry || size($objsToCache) == 1) {\n                attachOneCachePerGeometry(      $cacheFiles, $objsToCache,\n                                                                        $cacheDirectory, $action, $format );\n        } else {\n                if( size($cacheFiles) != 1 ) {\n                        error( (uiRes("m_doCreateGeometryCache.kInvalidCacheOptions")));\n                }\n\n                attachCacheGroups( $cacheFiles,$objsToCache,$cacheDirectory,$action, $format );\n\n        }\n\n        // If we\'re replacing a cache and inheriting modifications,\n        // restore the translation, scaling, clipping etc.\n        if( $action == "replace" && $inherit )\n        {\n                int $i = 0;\n                for( $i = 0; $i < size($objsToCache); $i++)\n                {\n                        string $cache[] = findExistingCaches($objsToCache[$i]);\n                        float $sStart = `getAttr ($cache[0]+".sourceStart")`;\n                        float $sEnd = `getAttr ($cache[0]+".sourceEnd")`;\n\n                        if( $sStart != $sourceStart[$i] &&\n                                $sourceStart[$i] >= $sStart &&\n                                $sourceStart[$i] <= $sEnd )\n                        {\n                                cacheClipTrimBefore( $cache[0], $sourceStart[$i] );\n                        }\n\n                        if( $sEnd != $sourceEnd[$i] &&\n                                $sourceEnd[$i] >= $sStart &&\n                                $sourceEnd[$i] <= $sEnd )\n                        {\n                                cacheClipTrimAfter( $cache[0], $sourceEnd[$i] );\n                        }\n\n                        setAttr ($cache[0] + ".startFrame") $startFrame[$i];\n                        setAttr ($cache[0] + ".scale") $scale[$i];\n                }\n        }\n        select -r $objsToCache;\n        return $cacheFiles;\n};'
doCreateGeometryCache3 = '\nglobal proc string[] doCreateGeometryCache3( int $version, string $args[] )\n//\n// Description:\n//\tCreate cache files on disk for the selected shape(s) according\n//  to the specified flags described below.\n//\n// A facsimle copy of doCreateGeometryCache just that args[6] i.e. export cache\n// per geometry is fixed to 1 regardless of group caching\n//\n// $version == 1:\n//\t$args[0] = time range mode:\n//\t\ttime range mode = 0 : use $args[1] and $args[2] as start-end\n//\t\ttime range mode = 1 : use render globals\n//\t\ttime range mode = 2 : use timeline\n//  $args[1] = start frame (if time range mode == 0)\n//  $args[2] = end frame (if time range mode == 0)\n//\n// $version == 2:\t\n//  $args[3] = cache file distribution, either "OneFile" or "OneFilePerFrame"\n//\t$args[4] = 0/1, whether to refresh during caching\n//  $args[5] = directory for cache files, if "", then use project data dir\n//\t$args[6] = 0/1, whether to create a cache per geometry\n//\t$args[7] = name of cache file. An empty string can be used to specify that an auto-generated name is acceptable.\n//\t$args[8] = 0/1, whether the specified cache name is to be used as a prefix\n// $version == 3:\n//  $args[9] = action to perform: "add", "replace", "merge", "mergeDelete" or "export"\n//  $args[10] = force save even if it overwrites existing files\n//\t$args[11] = simulation rate, the rate at which the cloth simulation is forced to run\n//\t$args[12] = sample mulitplier, the rate at which samples are written, as a multiple of simulation rate.\n//\n//  $version == 4:\n//\t$args[13] = 0/1, whether modifications should be inherited from the cache about to be replaced. Valid\n//\t\t\t\tonly when $action == "replace".\n//\t$args[14] = 0/1, whether to store doubles as floats\n//  $version == 5: \n//\t$args[15] = name of cache format\n//  $version == 6: \n//\t$args[16] = 0/1, whether to export in local or world space \n//\n{\t\n\tstring $cacheFiles[];\n\tif(( $version > 6 ) || ( size($args) > 17 )) {\n\t\terror( (uiRes("m_doCreateGeometryCache.kBadArgsError")));\n\t\treturn $cacheFiles;\n\t}\n\n\tstring  $cacheDirectory\t\t= "";\n\tstring\t$fileName\t\t\t= "";\n\tint\t\t$useAsPrefix\t\t= 0;\n\tint\t\t$perGeometry\t\t= 0;\n\tstring  $action        = "replace";\n\tint \t$force = 0;\n\tint\t\t$inherit = 0;\n\tint     $doubleToFloat = 0;\n\tstring $distribution = "OneFilePerFrame";\n\t\n\tint \t$rangeMode \t\t\t= $args[0];\n\tfloat  \t$diskCacheStartTime = $args[1];\n\tfloat  \t$diskCacheEndTime   = $args[2];\n\tfloat\t$simulationRate\t\t= 1.0;\n\tint\t\t$sampleMultiplier\t= 1;\n\t\n\tfloat  $startTime = $diskCacheStartTime;\n\tfloat  $endTime = $diskCacheEndTime;\n\tstring $format = "mcx";\t\t// Maya\'s default internal format\n\n\tint $worldSpace = 0;\n\n\tif( $rangeMode == 1 ) {\n        $startTime = `getAttr defaultRenderGlobals.startFrame`; \n        $endTime = `getAttr defaultRenderGlobals.endFrame`; \n\t} else if( $rangeMode == 2 ) {\n\t\t$startTime = `playbackOptions -q -min`;\n\t\t$endTime = `playbackOptions -q -max`;\n\t}\n\t\n\tif ($version > 1) {\n\t    $distribution = $args[3];\n\t\t$cacheDirectory = $args[5];\n\t\t$perGeometry = $args[6];\n\t\t$fileName = $args[7];\n\t\t$useAsPrefix = $args[8];\n\t}\n\tif ($version > 2) {\n\t\t$action = $args[9];\n\t\t$force = $args[10];\t\t\n\t\t\n\t\tif( size($args) > 11 ) {\n\t\t\t$simulationRate = $args[11];\n\t\t}\t\t\n\t\tif( size($args) > 12 ) {\n\t\t\t$sampleMultiplier = $args[12];\n\t\t}\n\t\telse {\n\t\t\t$sampleMultiplier = 1;\n\t\t}\n\t}\n\tif( $version > 3 ) {\n\t\t$inherit = $args[13];\n\t\t$doubleToFloat = $args[14];\n\t}\t\t\t\n\n\tif( $version > 4 ) {\n\t\t$format = $args[15];\n\t}\t\t\t\n\n\tif( $version > 5 ) {\n\t\t$worldSpace = $args[16];\n\t}\t\t\t\n\n\t// Call doMergeCache instead since it handles gaps between\n\t// caches correctly.\n\tif( $action == "merge" || $action == "mergeDelete" ) \n\t{\n\t\t\n\t\tstring $mergeArgs[];\n\t\t$mergeArgs[0] = 1;\n\t\t$mergeArgs[1] = $startTime;\n\t\t$mergeArgs[2] = $endTime;\n\t\t$mergeArgs[3] = $args[3];\n\t\t$mergeArgs[4] = $cacheDirectory;\n\t\t$mergeArgs[5] = $fileName;\n\t\t$mergeArgs[6] = $useAsPrefix;\n\t\t$mergeArgs[7] = $force;\n\t\t$mergeArgs[8] = $simulationRate;\n\t\t$mergeArgs[9] = $sampleMultiplier;\n\t\t$mergeArgs[10] = $action;\n\t\t$mergeArgs[11] = "geom";\n\t\t$mergeArgs[12] = $format;\n\t\treturn doMergeCache(2, $mergeArgs);\n\t}\n\t\n\t// If we\'re replacing a cache, and inheriting modifications, \n\t// the new cache should have the same translation, scaling \n\t// and clipping as the original. So store these values and \n\t// set after cache creation.\n\t//\n\tfloat $startFrame[] = {};\n\tfloat $sourceStart[] = {};\n\tfloat $sourceEnd[] = {};\n\tfloat $scale[] = {};\n\n\tselect -d `ls -sl -type cacheFile`;\n\tstring $objsToCache[] = getGeometriesToCache();\n\n\tif ($action == "add" ) {\n\t\tif (getCacheCanBeReplaced($objsToCache)) {\n\t\t\tif ( cacheReplaceNotAdd($objsToCache)) {\t\t\t\n\t\t\t\t$action = "replace";\n\t\t\t}\n\t\t}\n\t}\n\n\tif (size($objsToCache) == 0) {\n\t\terror((uiRes("m_doCreateGeometryCache.kMustSelectGeom")));\n\t} else \tif ($action == "replace") {\n\t\tif (!getCacheCanBeReplaced($objsToCache)) {\n\t\t\treturn $cacheFiles;\n\t\t}\n\t\t\n\t\tif( $inherit ) {\n\t\t\tstring $obj, $cache;\n\t\t\tfor( $obj in $objsToCache ) {\n\t\t\t\tstring $existing[] = findExistingCaches($obj);\n\t\t\t\tint $index = size($startFrame);\n\t\t\t\t$startFrame[$index] = `getAttr ($existing[0]+".startFrame")`;\n\t\t\t\t$sourceStart[$index] = `getAttr ($existing[0]+".sourceStart")`;\n\t\t\t\t$sourceEnd[$index] = `getAttr ($existing[0]+".sourceEnd")`;\n\t\t\t\t$scale[$index] = `getAttr ($existing[0]+".scale")`;\n\t\t\t}\n\t\t}\n\t}\n\n\t// If the user has existing cache groups on some of the geometry,\n\t// then they cannot attach new caches per geometry.\n\t//\n    string $cacheGroups[] = `getObjectsByCacheGroup($objsToCache)`;\n\tif (size($cacheGroups) != size($objsToCache)) {\n\t\t$perGeometry = 1;\n\t\t$args[6] = 1; // used below in generating cache file command\n\t\twarning( (uiRes("m_doCreateGeometryCache.kIgnoringPerGeometry")) );\n\t}\n\t\n\t// Check if directory has caches that might be overwritten\n\t//\n\tverifyWorkspaceFileRule( "fileCache", "cache/nCache" );\n\tstring $cacheDirectory = getCacheDirectory($cacheDirectory, "fileCache", \n\t\t\t\t\t\t\t\t\t\t\t\t$objsToCache, $fileName,\n\t\t\t\t\t\t\t\t\t\t\t\t$useAsPrefix, $perGeometry,\n\t\t\t\t\t\t\t\t\t\t\t\t$action, $force, 1);\n\n\tif ($cacheDirectory == "") {\n\t\treturn $cacheFiles;\n\t}\n\telse if ($cacheDirectory == "rename") {\n\t\tperformCreateGeometryCache 1 $action;\n\t\terror((uiRes("m_doCreateGeometryCache.kNameAlreadyInUse")));\n\t\treturn $cacheFiles;\n\t}\t\n\t\t\n\t// if we\'re replacing, delete active caches.\n\t//\n\tif( $action == "replace" ) {\n\t\tfor( $obj in $objsToCache ) {\n\t\t\tstring $all[] = findExistingCaches($obj);\n\t\t\tfor( $cache in $all) {\n\t\t\t\tif( `getAttr ($cache+".enable")`) {\n\t\t\t\t\tdeleteCacheFile(2, {"keep",$cache});\n\t\t\t\t}\n\t\t\t}\n\t\t}\n\t}\n\n\t// create the cache(s)\n\t//\n\tif ($action == "add" || $action == "replace") {\n\t\tsetCacheEnable(0, 1, $objsToCache);\n\t}\n\t\n\t// generate the cacheFile command to write the caches\n\t//\n\tstring $cacheCmd = getCacheFileCmd($version, $cacheDirectory, $args);\n\tint $ii = 0;\n\t\n\t//segmented cache files are employed in the case of one large cache file that\n\t//exceeds 2GB in size.  Since we currently cannot handle such large files, we will\n\t//automatically generate several caches, each less than 2GB.\n\tint $useSegmentedCacheFile = 0;\n\tint $numSegments = 0; \n\tif($distribution == "OneFile" && !$perGeometry) {\n\t    string $queryCacheSizeCmd = "cacheFile";\n\t    for ($ii = 0; $ii < size($objsToCache); $ii++) {\n\t\t    $queryCacheSizeCmd += (" -points "+$objsToCache[$ii]);\n\t    }\n\t    $queryCacheSizeCmd += " -q -dataSize";\n\t    if($doubleToFloat) {\n\t        $queryCacheSizeCmd += " -dtf";\n\t    }\n\t    float $dataSizePerFrame = `eval $queryCacheSizeCmd`;\n\t    float $maxSize = 2147000000; //approximate size of max signed int.\n\t    float $numSamples = ($endTime - $startTime + 1.0)/($simulationRate*$sampleMultiplier);\n\t    float $dataSize = $dataSizePerFrame*$numSamples;\n\t    if($dataSize > $maxSize) {\n\t        $useSegmentedCacheFile = 1;\n\t        $numSegments = floor($dataSize / $maxSize) + 1;\t        \t        \t        \n\t    }\n\t}\n\t\n\tif(!$useSegmentedCacheFile) {\t\t\n\t    if( $fileName != "" ) {\n\t\t    $cacheCmd += ("-fileName \\"" + $fileName + "\\" ");\n\t    }\n\t    $cacheCmd += ("-st "+$startTime+" -et "+$endTime);\n\n\t    // if we\'re exporting vertex data only, can do it in world space too\t\t    \n\t    if(($action == "export") && size($objsToCache) > 0 && $worldSpace > 0 ) {\n\t    \t    $cacheCmd += (" -worldSpace ");\n\t    }\n\n\t    for ($ii = 0; $ii < size($objsToCache); $ii++) {\n\t\t    $cacheCmd += (" -points "+$objsToCache[$ii]);\n\t    }\n\t    $cacheFiles = `eval $cacheCmd`;\n\t}\n\telse {\n\t    int $jj;\n\t    float $segmentStartTime = $startTime;\n\t    float $segmentEndTime;\n\t    float $segmentLength = ($endTime - $startTime)/$numSegments;\n\t    string $segmentCacheCmd ;\n\t    string $segmentCacheName = "";\n\t    string $segmentCacheFiles[];\n\t    for($jj = 0; $jj< $numSegments; $jj++) {\t        \n\t        $segmentCacheCmd = $cacheCmd;\n\t        if($fileName != "") \n\t            $segmentCacheName = $fileName;\t        \t        \n\t        else\n\t            $segmentCacheName = getAutomaticCacheName();\n\t        $segmentEndTime = $segmentStartTime + floor($segmentLength);\t       \t        \n\t        \t        \n\t        $segmentCacheName += ("Segment" + ($jj+1));\n\t        $segmentCacheCmd += (" -fileName \\"" + $segmentCacheName + "\\" ");\t        \n\t        \t          \n\t        $segmentCacheCmd += ("-st "+$segmentStartTime+" -et "+$segmentEndTime);\n\t    \n\t   \t// if we\'re exporting vertex data only, can do it in world space too\t\t    \n\t    \tif(($action == "export") && size($objsToCache) > 0 && $worldSpace > 0 ) {\n\t    \t   \t$segmentCacheCmd += (" -worldSpace ");\n\t   \t}\n\n\t        for ($ii = 0; $ii < size($objsToCache); $ii++) {\n\t\t        $segmentCacheCmd += (" -points "+$objsToCache[$ii]);\n\t        }\n\t        $segmentCacheFiles = `eval $segmentCacheCmd`;\n\t        $segmentStartTime = $segmentEndTime + 1;\n\t        \n\t        $cacheFiles[size($cacheFiles)] = $segmentCacheFiles[0];\n\t    }\t    \n    }\n\n\tif ($action == "export") {\n\t\tfor ($ii = 0; $ii < size($cacheFiles); $ii++) {\n\t\t\t$cacheFiles[$ii] = ($cacheDirectory+"/"+$cacheFiles[$ii]+".xml");\n\t\t}\n\t\t// In export mode, we do not want to attach the cache. We are done.\n\t\t//\n\t\treturn $cacheFiles;\n\t}\n\t\n\t\t\n\t// attach the caches to the history switch\n\t//\n\tif($useSegmentedCacheFile) {\n\t    if(size($objsToCache) == 1) {\n\t        for($ii=0;$ii<size($cacheFiles);$ii++) {\n\t            string $segmentCacheFile[];\n\t            $segmentCacheFile[0] = $cacheFiles[$ii];\n\t            attachOneCachePerGeometry( \t$segmentCacheFile, $objsToCache, \n\t\t\t\t\t\t\t\t\t$cacheDirectory, $action, $format );\n\t        }\n\t    }\n\t    else {\n\t        for($ii=0;$ii<size($cacheFiles);$ii++) {\n\t            string $segmentCacheFile[];\n\t            $segmentCacheFile[0] = $cacheFiles[$ii];\n\t            attachCacheGroups( $segmentCacheFile,$objsToCache,$cacheDirectory,$action, $format );\n\t        }\t        \n\t    }\n\t    \n\t}\n\telse if( $perGeometry || size($objsToCache) == 1) {\n\t\tattachOneCachePerGeometry( \t$cacheFiles, $objsToCache, \n\t\t\t\t\t\t\t\t\t$cacheDirectory, $action, $format );\n\t} else {\n\t\tif( size($cacheFiles) != 1 ) {\n\t\t\terror( (uiRes("m_doCreateGeometryCache.kInvalidCacheOptions")));\n\t\t}\n\t\t\n\t\tattachCacheGroups( $cacheFiles,$objsToCache,$cacheDirectory,$action, $format );\t\t\n\t\t\n\t}\n\n\t// If we\'re replacing a cache and inheriting modifications,\n\t// restore the translation, scaling, clipping etc.\n\tif( $action == "replace" && $inherit ) \n\t{\n\t\tint $i = 0;\n\t\tfor( $i = 0; $i < size($objsToCache); $i++) \n\t\t{\n\t\t\tstring $cache[] = findExistingCaches($objsToCache[$i]);\n\t\t\tfloat $sStart = `getAttr ($cache[0]+".sourceStart")`;\n\t\t\tfloat $sEnd = `getAttr ($cache[0]+".sourceEnd")`;\n\t\t\t\n\t\t\tif( $sStart != $sourceStart[$i] &&\n\t\t\t\t$sourceStart[$i] >= $sStart &&\n\t\t\t\t$sourceStart[$i] <= $sEnd )\n\t\t\t{\n\t\t\t\tcacheClipTrimBefore( $cache[0], $sourceStart[$i] );\n\t\t\t}\n\t\t\t\n\t\t\tif( $sEnd != $sourceEnd[$i] &&\n\t\t\t\t$sourceEnd[$i] >= $sStart &&\n\t\t\t\t$sourceEnd[$i] <= $sEnd )\n\t\t\t{\n\t\t\t\tcacheClipTrimAfter( $cache[0], $sourceEnd[$i] );\n\t\t\t}\n\t\t\t\n\t\t\tsetAttr ($cache[0] + ".startFrame") $startFrame[$i];\n\t\t\tsetAttr ($cache[0] + ".scale") $scale[$i];\n\t\t}\n\t}\n\tselect -r $objsToCache;\n\treturn $cacheFiles;\n}\n'
pc.Mel.eval(doCreateGeometryCache2)
pc.Mel.eval(doCreateGeometryCache3)
# okay decompiling __init__.pyc
