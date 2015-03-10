import os
from os import walk
from xml.etree.ElementTree import parse
import json
import re
from collections import OrderedDict


class Swbdnext(str):

    """this class' purpose is to extract maeningful features
    realed to prominence preditions. It extracts word, phonwords
    dialAct, kontrast, disfluency, phrases, and accent level
    features"""

    def __init__(self, str):

        self.path = str
        try:
            tree = parse(self.path)
        except:
            raise "Error"
        self.root = tree.getroot()
        self.filename = re.findall("sw\d+\w+.[AB].", self.path)[0]
        self.supfolder = re.findall("(\S+/xml/)", self.path)[0]
        self.suffix = '.xml'
        self.trace = 0  # location of file chunck, phonewords
        self.traceDia = 0  # location of file chunck, dialAct
        self.tracekont = 0  # location of file chunck, kontrast
        self.tracephrase = 0  # location of file chunck,phrases
        self.traceacc = 0  # location of file chunck, accents
        self.kontrast_root = None
        self.phrase_root = None
        self.accent_root = None
        self.disfluency_tree = None
        self.phonwords_root = None
        self.dialAct_root = None
        self.disf_dict = {}
        self.outdir =  "../processed_swbd/" + self.filename
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)  

    def terminals(self):
        """extract terminals info; word, tag, timings, swbd id"""

        for (k,child) in enumerate(self.root):
            self.current_word = []
            if child.tag == "word":
                word_d = child.attrib
                self.word_id = word_d["{http://nite.sourceforge.net/}id"]
                self.disfluency()  # extract disfluency
                self.current_word.append(("word", word_d["orth"]))
                self.current_word.append(("tag", word_d["pos"]))
                self.current_word.append(
                    ("start", word_d["{http://nite.sourceforge.net/}start"]))
                self.current_word.append(
                    ("end", word_d["{http://nite.sourceforge.net/}end"]))
                self.current_word.append(
                    ("id", word_d["{http://nite.sourceforge.net/}id"]))
                self.dialAct()  # extract dialAct
                self.kontrast()  # extract kontrast
                try:
                    for child2 in child:
                        # refer to phonwords and copy final_word to jason
                        self.phonwords(child2.attrib["href"])
                        with open(self.outdir+'/'+str(k) ,'w') as fjson:
                            json.dump(OrderedDict(self.current_word), fjson, indent=4)                            
                except:
                    # no children
                    with open(self.outdir+'/'+str(k) ,'w') as fjson:
                        json.dump(OrderedDict(self.current_word), fjson, indent=4)   
                slist = self.filename+"D"+self.word_id+'D'+self.current_word[0][1]
                flist.write(slist)
                flist.write('\n')

            elif child.tag == "sil":
                pass

    def phonwords(self, subpath=""):
        """extract phonwords info; subword, syll stresses, num of sylls"""

        if subpath:  # not the highest in hirarchy
            if self.trace == 0:
                full_sub = self.supfolder + "phonwords/" + \
                    subpath.split('#')[0]  # detect file
                tree = parse(full_sub)
                self.phonwords_root = tree.getroot()

            # detect phonwords id
            ids = re.findall("\((\w+)\)", subpath.split('#id')[1])
            if len(ids) > 1:
                match = re.findall("\d+", ' '.join(ids))
                if int(match[3]) - int(match[1]) > 1:
                    ids = self.scrollit(ids)  # make refs explicit

            flag = 0
            for val in ids:
                for (i, child) in enumerate(self.phonwords_root[self.trace:self.trace + 50]):
                    d_phonword = child.attrib
                    if d_phonword["{http://nite.sourceforge.net/}id"] == val:
                        flag = 1
                        self.current_word.append(
                            ("subword", d_phonword["orth"]))
                        try:
                            # if info on stress found
                            self.current_word.append(
                                ("stressProfile", d_phonword["stressProfile"]))
                            self.current_word.append(
                                ("num_sylls", len(d_phonword["stressProfile"])))
                            self.phrases(val)
                            self.accents(val)
                            break
                        except:
                            # not found in syll xml as well
                            self.current_word.append(
                                ("stressProfile", "unknown"))
                            self.current_word.append(("num_sylls", "unknown"))
                            self.phrases(val)
                            self.accents(val)
                            break

            self.trace += i
            if not flag:
                print "not found"

        elif self.path:  # the highest in hirarchy
            self.phonwords_root = self.root
            # TBD if needed
        else:
            raise "Error"  # something is wrong

    def dialAct(self):
        """extract dialAct info; nite_type"""

        if self.traceDia == 0:  # set path
            dialAct_path = self.supfolder + "dialAct/" + \
                self.filename + "dialAct" + self.suffix
            tree = parse(dialAct_path)
            self.dialAct_root = tree.getroot()

        flag = 0
        for (i, child) in enumerate(self.dialAct_root[self.traceDia:self.traceDia + 50]):
            d_dialAct0 = child.attrib
            for child2 in child:
                d_dialAct = child2.attrib  # match the word id with child id
                if d_dialAct["href"].rstrip(')').split('(')[1] == self.word_id:
                    flag = 1
                    self.current_word.append(
                        ("dialAct:niteType", d_dialAct0["niteType"]))
                    self.current_word.append(
                        ("dialAct:id", d_dialAct0["{http://nite.sourceforge.net/}id"]))                    
                    break
            if flag:
                break
        if i is not 49:
            self.traceDia += i
        if i == 49:
            # print self.word_id
            # print "not found"
            pass

    def kontrast(self):
        """extract kontrast info; type, level"""

        if self.kontrast_root is None:  # set path
            kontrast_path = self.supfolder + "kontrast/" + \
                self.filename[:-2] + "kontrast" + self.suffix
            try:  # not available for all data
                tree = parse(kontrast_path)
                self.kontrast_root = tree.getroot()
            except:
                return

        if self.kontrast_root is not None:  # tree was extracted
            flag = 0
            for (i, child) in enumerate(self.kontrast_root[self.tracekont:self.tracekont + 50]):
                d_kontrast0 = child.attrib
                for child2 in child:
                    # match the word id with child id
                    d_kontrast = child2.attrib
                    if d_kontrast["href"].rstrip(')').split('(')[1] == self.word_id:
                        flag = 1
                        self.current_word.append(
                            ("kontrast:level", d_kontrast0["level"]))
                        self.current_word.append(
                            ("kontrast:type", d_kontrast0["type"]))
                        break
                if flag:
                    break
            if i is not 49:
                self.tracekont += i
            if i == 49:  # don't progress tracer since not found in file
                # print self.word_id
                # print "not found"
                pass

    def disfluency(self):
        """extract disfluency info; creates a dict with every
        terminal referenced and its type on first iteration.
        Then checks termianl type according to dict every iteration"""

        if self.disfluency_tree is None:  # set path
            disfluency_path = self.supfolder + "disfluency/" + \
                self.filename + "disfluency" + self.suffix
            self.disfluency_tree = parse(disfluency_path)
            first = 1
        else:
            first = 0

        if first:
            event = []
            first1 = 0
            # extract all terminal refs defaut type "repara"
            for elem in self.disfluency_tree.iter():
                if elem.tag == "{http://nite.sourceforge.net/}child":
                    self.disf_dict[elem.attrib["href"].rstrip(')').split(
                        '(')[1]] = "reparandum"
                elif first1:
                    event.append(
                        elem.attrib["{http://nite.sourceforge.net/}id"])
                first1 = 1

            # extract all repair and modify dict accordingly
            for elem in self.disfluency_tree.iter("repair"):
                id_rp = elem.attrib["{http://nite.sourceforge.net/}id"]
                sub_num = len(id_rp.split('.'))

                if sub_num == 4:
                    for child in elem:
                        if child.tag == "{http://nite.sourceforge.net/}child":
                            self.disf_dict[child.attrib["href"].rstrip(')').split(
                                '(')[1]] = "repair"
                # if is found in sub hirarchy, check if ancestors are repair as
                # well
                else:
                    for i in xrange(sub_num):
                        new_rp = id_rp.rsplit(".", 2)[0]
                        idx = event.index(new_rp)
                        # print new_rp
                        if "reparandum" in event[idx + 1]:
                            # print event[idx+1]
                            break
                        else:
                            id_rp = event[idx + 1]

        try:  # check termianl type
            self.current_word.append(
                ("disf_stat", self.disf_dict[self.word_id]))
        except:
            self.current_word.append(("disf_stat", "none"))

    def scrollit(self, idx):
        """explicity list all reference: e.g. 2 reference pointers
        of idx = ['ms44B_pw99', 'ms44B_pw102'] will be converted
        to idx =['ms44B_pw99', 'ms44B_pw100', 'ms44B_pw101', 'ms44B_pw102']"""

        match = re.findall("\d+", ' '.join(idx))
        gap = int(match[3]) - int(match[1])
        digit = len(match[1])
        subid = [idx[0]]
        for i in xrange(gap - 1):
            added_value = str(int(i + 1 + int(idx[0][-digit:])))
            if len(added_value) > digit:
                subid.append(idx[1][:-(digit + 1)] + added_value)
            else:
                subid.append(idx[0][:-(digit)] + added_value)
        subid.append(idx[1])
        idx = subid
        return idx

    def phrases(self, phonword_id):
        """extract phrases info; type"""

        if self.phrase_root is None:  # set path
            phrase_path = self.supfolder + "phrase/" + \
                self.filename + "phrases" + self.suffix
            try:  # not available for all data
                tree = parse(phrase_path)
                self.phrase_root = tree.getroot()
            except:
                return

        if self.phrase_root is not None:  # was open already
            flag = 0
            for (i, child) in enumerate(self.phrase_root[self.tracephrase:self.tracephrase + 50]):
                d_phrase0 = child.attrib
                for child2 in child:
                    d_phrase = child2.attrib  # match the word id with child id
                    # detect phonwords id
                    ids = re.findall("\((\w+)\)", d_phrase["href"])
                    if len(ids) > 1:
                        match = re.findall("\d+", ' '.join(ids))
                        if int(match[3]) - int(match[1]) > 1:
                            ids = self.scrollit(ids)  # make refs explicit
                            # print ids
                    for val in ids:
                        if val == phonword_id:
                            flag = 1
                            self.current_word.append(
                                ("phrases:type", d_phrase0["type"]))
                            break
                    if flag:
                        break
                if flag:
                    break

            if i is not 49:
                self.tracephrase += i
            if i == 49:
                # print phonword_id
                # print "not found"
                pass

    def accents(self, phonword_id):
        """extract accents info; strength"""

        if self.accent_root is None:  # set path
            accents_path = self.supfolder + "accent/" + \
                self.filename + "accents" + self.suffix
            try:  # not available for all data
                tree = parse(accents_path)
                self.accent_root = tree.getroot()
            except:
                return

        if self.accent_root is not None:
            flag = 0
            for (i, child) in enumerate(self.accent_root[self.traceacc:self.traceacc + 50]):
                d_accent0 = child.attrib
                for child2 in child:
                    d_accent = child2.attrib  # match the word id with child id
                    # detect phonwords id
                    ids = re.findall("\((\w+)\)", d_accent["href"])
                    if len(ids) > 1:  # less common to be as part of a sequence
                        match = re.findall("\d+", ' '.join(ids))
                        if int(match[3]) - int(match[1]) > 1:
                            ids = self.scrollit(ids)  # make refs explicit
                    for val in ids:
                        if val == phonword_id:
                            flag = 1
                            self.current_word.append(
                                ("accents:strength", d_accent0["strength"]))
                            break
                    if flag:
                        break
                if flag:
                    break

            if i is not 49:
                self.traceacc += i
            if i == 49:
                # print phonword_id
                # print "not found"
                pass

mypath = '../../swbd_next/nxt/xml/terminals/'  # path to swbd terminals
f = []
#for (dirpath, dirnames, filenames) in walk(mypath):
    #f.extend(filenames)
    #break
# idd = filenames.index("sw2018.A.terminals.xml")
# filenames=filenames[idd:]
#filenames = ["sw2060.A.terminals.xml"]
lst = open("../config/for_proc_swbd","r")
filenames = lst.readlines()
flist = open("list_nxt_files","w")
for filename in filenames:
    Swbdnext(mypath + filename[:-1]).terminals()
