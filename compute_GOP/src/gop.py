from extract_mat import load_likelihood
from numerator import compute_numrator
from denominator import compute_denominator
from plain_sum import comute_final
from dictit import dict_phones, dict_pdfs

# grep -o -r "\w*xx\w*" . 
#bestfiles = "../files/Phonelat"

path = "../files/letter_mod_exp/"
likefiles = path+"likelihood1"
pdffiles_n = path+"num_pdf"
durfiles_n = path+"num_dur"
pdffiles_d = path+"den_pdf"
durfiles_d = path+"den_dur"
filelist = path+"all2.txt"
outfolder = path+"out_orig_txt/"
phones = path+"phones.txt"
pdfs = path+"pdf2phn.txt"

out_fols = ["vt_sum/", "vt_max/", "ratio/"]
num2phone = dict_phones(phones)
pdf2phone = dict_pdfs(pdfs)

  

# for file; write filename:
for mode in [1, 2, 3]:
    fall = open(filelist,"r")    
    print mode
    mode = 2
    outfolderM = outfolder+out_fols[mode-1]
    for filename in fall.readlines():
        filename = "10_3_ksa3wxx0_000020-000024"
        filename = filename.replace("\n","")
        ll_mat = load_likelihood(filename, likefiles)
        ph_sum_dur, pd_ll = compute_numrator(ll_mat, filename, pdffiles_n, durfiles_n, mode) 
        sum_dur = compute_denominator(ll_mat, filename, pdffiles_d, durfiles_d, ph_sum_dur[:,2], mode) 
        
        with open(outfolderM+filename, "w") as fout:
            # should be converted to phn_id 
            #(now represented as pdf_id of a phoneme)
            fout.write(filename)
            fout.write("\n")
            if mode==1: # computes the ll of all sequence
                for r in xrange(len(ph_sum_dur)):
                    
                    pdf_id = ph_sum_dur[r,0]
                    num = pdf2phone[int(pdf_id)]
                    phone = num2phone[num]
                    
                    
                    
                    fout.write(
                        "{0} {1}".format(
                            str(phone).ljust(5),
                            str(ph_sum_dur[r,1]-sum_dur[r,0]).rjust(15),
                            )
                        )                 
                    fout.write("\n")            
                fout.close()
            if mode==2: # computes ll with the longest sequence 
                for r in xrange(len(ph_sum_dur)):
                    
                    pdf_id = ph_sum_dur[r,0]
                    num = pdf2phone[int(pdf_id)]
                    phone = num2phone[num]
                    
                    fout.write(
                        "{0} {1} {2} {3}".format(
                            str(phone).ljust(5),
                            str(ph_sum_dur[r,1]-sum_dur[r,0]).rjust(15),
                            str(int(ph_sum_dur[r,2])).rjust(5),
                            str(int(sum_dur[r,1])).rjust(5)
                            )
                        )                           
                    fout.write("\n")            
                fout.close()  
                
            if mode==3: # divedes every nomerator ll in sum of denominator ll
                phn, final_score = comute_final(ph_sum_dur, pd_ll, sum_dur)
                for r in xrange(len(final_score)):
                    
                    pdf_id = phn[r]
                    num = pdf2phone[int(pdf_id)]
                    phone = num2phone[num]    
                    
                    fout.write(
                        "{0} {1}".format(
                            str(phone).ljust(5),
                            str(final_score[r]).rjust(15),
                            )
                        )                 
                    fout.write("\n")            
                fout.close()  
    fall.close()
            
