from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


class Similarity():
    @classmethod
    def cosine_similariy(cls, Titles):
        titles = Titles
        vect = TfidfVectorizer(min_df=1)
        tfidf = vect.fit_transform(titles)
        T_tfidf = tfidf.T
        simi = (tfidf * T_tfidf).A
        R_simi = np.round(simi, 3)

        # if semicent is above 70%, cont adds 1 for title[i]
        fre = []
        index_to_remove = []
        for i in range(len(R_simi)):
            cont = 1
            for j in range(len(R_simi[i])):
                if R_simi[i][j] >= 0.7 and j != i:
                    cont += 1
                    index_to_remove.append((str(i), str(j)))
            fre.append(cont)

        title_fre = []
        for i in range(len(titles)):
            title_fre.append((titles[i], fre[i]))
        cls.titlefre_dic = dict()
        for i in range(len(title_fre)):
            cls.titlefre_dic[title_fre[i][0]] = [title_fre[i][1]]
        cls.titlefre_dic

        cls.titlest = Titles
        R_simit = R_simi
        flag1 = True
        while (flag1):
            flag2 = False
            for i in range(len(R_simit)):
                if (flag2):
                    break
                else:
                    for j in range(len(R_simit[i])):
                        # if similarity bigger than 70% & not the same value in column vector and row vector, consider as relevant duplicated titles
                        if R_simit[i][j] >= 0.5 and j != i:
                            del cls.titlest[j] # eliminate duplicates
                            flag2 = True # back to while loop, i and j restart from 0
                            vect = TfidfVectorizer(min_df=1)
                            tfidf = vect.fit_transform(cls.titlest)
                            T_tfidf = tfidf.T
                            simit = (tfidf * T_tfidf).A
                            R_simit = np.round(simit, 3)
                            #print(len(R_simit))
                            #print(titlest)
                            break
            if (i == (len(R_simit) - 1)): # if i reaches the last element of R_simit list, flag1 stops while loop
                flag1 = False

    @classmethod
    def get_simi_titlefre(cls, Titles):
            titles_sgt = Titles
            Similarity.cosine_similariy(titles_sgt)
            titlest_sgt = cls.titlest
            simi_titlefre = {titl: cls.titlefre_dic[titl] for titl in titlest_sgt}  # data = {'a':1,'b':2,'c':3}
            return simi_titlefre

