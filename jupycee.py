from IPython.core.ultratb import AutoFormattedTB
from IPython.core.display import display, HTML
import re
import requests
from sty import fg, bg, ef, rs
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.luhn import LuhnSummarizer

itb = AutoFormattedTB(mode = 'Plain', tb_offset = 1)


def custom_exc(shell, etype, evalue, tb, tb_offset=None):

    # Default msg
    #shell.showtraceback((etype, evalue, tb), tb_offset=tb_offset)

    
    stb = itb.structured_traceback(etype, evalue, tb)
    sstb = itb.stb2text(stb)

    print (sstb) 
    errorName = str(etype)
    fullSentence = str(evalue)
    elist = re.findall("\'(.*?)\'",errorName)
    json1 = make_request(elist[0],fullSentence)

    if(json1 !="NA"):
        
        url,que,ans = get_urls(json1)
        printext = bg.blue + "Answer Found" + bg.rs
        print(printext)
        print("Url is "+url[0])
        print("Que id is "+str(que[0]))
        print("Ans id is "+str(ans[0]))

        x=str(que[0])
        z=ans[0]
        y=make_request_ques(x)
        for i in y['items']:
            if(i['answer_id']==z):
                printext = bg.blue + "Un-summarised Answer is" + bg.rs
                print(printext)
                display(HTML(i['body']))
                a=re.split(r'[.!?]+', i['body'])
                if(len(a)>5):
                    printext = bg.blue + "Summarised" + bg.rs
                    print(printext)
                    # For Strings
                    parser=PlaintextParser.from_string(i['body'],Tokenizer("english"))
                    # Using KL
                    summarizer = LuhnSummarizer()
                    #Summarize the document with 4 sentences
                    summary = summarizer(parser.document,4)
                    allS=""
                    for sentence in summary:
                        allS = allS+str(sentence)
                    display(HTML(allS))
                else:
                    printext = bg.red + "No Summarisation needed due to less sentences founnd in the answer" + bg.rs
                    print(printext)
                    
    else:
        print("No Answer Found In stackOverFlow For This Erorr")
    

get_ipython().set_custom_exc((Exception,), custom_exc)

def make_request(name,fullS):
    
    allQuery = name + ": " + fullS
    #print(name)
    #print(fullS)
    printext = fg.green + "Searching for "+allQuery+ fg.rs
    print(printext)
    resp  = requests.get("https://api.stackexchange.com/"+"/2.2/search?order=desc&sort=votes&tagged=python&intitle={}&site=stackoverflow".format(allQuery))
    respJson = resp.json()
    if(len(respJson['items'])==0):
        
        printext = fg.red + "No search result found for"+ allQuery + fg.rs
        print(printext)
        printext = fg.green + "Searching for "+fullS + fg.rs
        print(printext)
        resp  = requests.get("https://api.stackexchange.com/"+"/2.2/search?order=desc&sort=votes&tagged=python&intitle={}&site=stackoverflow".format(fullS))
        respJson = resp.json()
        
    if(len(respJson['items'])==0):
        printext = fg.red + "No search result found for: "+fullS + fg.rs
        print(printext)
        printext = fg.green + "Searching for: "+name + fg.rs
        print(printext)
        resp  = requests.get("https://api.stackexchange.com/"+"/2.2/search?order=desc&sort=votes&tagged=python&intitle={}&site=stackoverflow".format(name))
        respJson = resp.json()
        
    if(len(respJson['items'])==0):
        printext = fg.red + "No search result found for: "+name + fg.rs
        print(printext)
        print("Ending Search")
        print(respJson)
        respJson = "NA"
        
    return respJson

def make_request_ques(idq):
    resp  = requests.get("https://api.stackexchange.com/"+"/2.2/questions/{}/answers?order=desc&sort=activity&site=stackoverflow&filter=withbody".format(idq))
    return resp.json()


def get_urls(json_dict):
    url_list = []
    ans_list = []
    que_list = []
    count = 0
    
    for i in json_dict['items']:
        if("accepted_answer_id" in i):
            url_list.append(i["link"])
            ans_list.append(i["accepted_answer_id"])
            que_list.append(i["question_id"])
            count+=1
        if count == len(i) or count == 100:
            break
    return url_list,que_list,ans_list