from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


class Similarity:
    @classmethod
    def cosine_similariy(cls, Titles):
        titles = Titles  # make copy of title
        vect = TfidfVectorizer(min_df=1)
        tfidf = vect.fit_transform(titles)
        T_tfidf = tfidf.T
        simi = (tfidf * T_tfidf).A  # matrix.A: Return self as an ndarray object
        R_simi = np.round(simi, 3)

        '''
        # index of column vector & row vector:(i,index), and value it accomodates:simicent
        for i in range(len(R_simi)):
            for index,simicent in enumerate(R_simi[i]):
                print(str(i)+str(index),simicent)
        '''

        # if semicent is above 70%, cont adds 1 for title[i]
        fre = []
        index_to_remove = []  # store index of title intended to remove
        for i in range(len(R_simi)):
            cont = 0
            for j in range(len(R_simi[i])):
                if R_simi[i][j] >= 0.7 and j != i:  # if similarity bigger than 70% & not the same value in column vector and row vector, consider as relevant titles
                    cont += 1
                    index_to_remove.append((str(i), str(j)))  # get index pair of two relevant news title
            fre.append(cont)  # relevant frequency of each title to all stored in "titles" list
        # print(fre)
        # print(index_to_remove)


        # dictionary news title and title frequency
        title_fre = []
        for i in range(len(titles)):
            title_fre.append((titles[i], fre[i]))
        cls.titlefre_dic = dict()
        for i in range(len(title_fre)):
            cls.titlefre_dic[title_fre[i][0]] = [title_fre[i][1]]
        cls.titlefre_dic # store each news title and its frequency in dict

        # remove relevant title duplicates
        cls.titlest = Titles # make a copy of titles, elements after manipulating be stored
        R_simit = R_simi # make a copy of R_simi
        flag1 = True # flag1 control while loop
        while (flag1):
            flag2 = False # flag2 control for loop
            for i in range(len(R_simit)):
                if (flag2):
                    break
                else:
                    for j in range(len(R_simit[i])):
                        # if similarity bigger than 70% & not the same value in column vector and row vector, consider as relevant duplicated titles
                        if R_simit[i][j] >= 0.7 and j != i:
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

        # rearrange dictionary news title & title frequency after similarity frequency sorting

    @classmethod
    def get_simi_titlefre(cls, Titles):
            titles_sgt = Titles
            Similarity.cosine_similariy(titles_sgt)
            titlest_sgt = cls.titlest
            simi_titlefre = {titl: cls.titlefre_dic[titl] for titl in titlest_sgt}  # data = {'a':1,'b':2,'c':3}
            return simi_titlefre

