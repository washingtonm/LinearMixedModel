__author__ = 'Haohan Wang'

import sys

sys.path.append('../')

from dataLoader import GenLoading, EEGLoading, EEGLoadingKSU, GenLoadingKSU, RanLoading, RanLoadingKSU
from LMM.lmm_lasso import *
from LMM.lmm_lassoMulti import *
from evaluation import precision_recall

methods = ['linear', 'lasso', 'ridge']


def runEEG(numintervals=100, ldeltamin=-5, ldeltamax=5, nums=10000, z=0):
    X, y, Z0, Z1 = EEGLoading()


    for i in range(5):
        if i != 3:
            print 'con ', i
            if i == 0:
                K = np.dot(Z0, Z0.T)
            elif i == 1:
                K = np.dot(Z1, Z1.T)
            elif i == 2:
                Z2 = np.append(Z0, Z1, 1)
                K = np.dot(Z2, Z2.T)
            else:
                Z2 = Z0 + Z1
                K = np.dot(Z2, Z2.T)
            Kv = K[nums:, nums:]
            K = K[:nums, :nums]
            S, U = np.linalg.eigh(K)
            Sv, Uv = np.linalg.eigh(Kv)

            for REML in [True, False]:
                for l in range(2):
                    print 'EEG label', l
                    Y = y[:, l]

                    Xtr = X[:nums, :]
                    Ytr = Y[:nums]
                    Xte = X[nums:, :]

                    print 'linear'
                    w_linear, alp, l_linear, clf_linear = train(Xtr, K, Ytr, mu=0, numintervals=numintervals, ldeltamin=ldeltamin,
                                                                ldeltamax=ldeltamax, method='linear', selectK=False, regression=False, REML=REML, S=S, U=U)
                    print 'lasso'
                    w_lasso, alp, l_lasso, clf_lasso = train(Xtr, K, Ytr, mu=0, numintervals=numintervals, ldeltamin=ldeltamin,
                                                             ldeltamax=ldeltamax, method='lasso', selectK=False, regression=False, REML=REML, S=S, U=U)
                    print 'ridge'
                    w_rd, alp, l_rd, clf_rd = train(Xtr, K, Ytr, mu=0, numintervals=numintervals, ldeltamin=ldeltamin,
                                                    ldeltamax=ldeltamax, method='ridge', selectK=False, regression=False, REML=REML, S=S, U=U)

                    y_pred_linear = predict(Xte, Sv, Uv, l_linear, clf_linear)
                    y_pred_lasso = predict(Xte, Sv, Uv, l_lasso, clf_lasso)
                    y_pred_rd = predict(Xte, Sv, Uv, l_rd, clf_rd)

                    m = []
                    m.append(y_pred_linear)
                    m.append(y_pred_lasso)
                    m.append(y_pred_rd)
                    m = np.array(m)
                    if REML:
                        np.savetxt('../results'+str(z)+'/EEGResult_REML_label_'+str(l+1)+'_con_'+str(i+1)+'.csv', m, delimiter=',')
                    else:
                        np.savetxt('../results'+str(z)+'/EEGResult_ML_label_'+str(l+1)+'_con_'+str(i+1)+'.csv', m, delimiter=',')

    print 'con 3'

    K0 = np.dot(Z0, Z0.T)
    K1 = np.dot(Z1, Z1.T)

    KList = [K0[:nums, :nums], K1[:nums, :nums]]
    S0, U0 = np.linalg.eigh(KList[0])
    S1, U1 = np.linalg.eigh(KList[1])
    SList = [S0, S1]
    UList = [U0, U1]
    KvList = [K0[nums:, nums:], K1[nums:, nums:]]
    Sv0, Uv0 = np.linalg.eigh(KvList[0])
    Sv1, Uv1 = np.linalg.eigh(KvList[1])
    SvList = [Sv0, Sv1]
    UvList = [Uv0, Uv1]


    for REML in [True, False]:
        for l in range(2):
            print 'EEG label', l
            Y = y[:, l]
            Xtr = X[:nums, :]
            Ytr = Y[:nums]
            Xte = X[nums:, :]

            print 'linear'
            w_linear, alp, l_linear, clf_linear = trainMulti(Xtr, KList, Ytr, mu=0, numintervals=numintervals, ldeltamin=ldeltamin,
                                                        ldeltamax=ldeltamax, method='linear', selectK=False, regression=False, SList=SList, UList=UList)
            print 'lasso'
            w_lasso, alp, l_lasso, clf_lasso = trainMulti(Xtr, KList, Ytr, mu=0, numintervals=numintervals, ldeltamin=ldeltamin,
                                                     ldeltamax=ldeltamax, method='lasso', selectK=False, regression=False, SList=SList, UList=UList)
            print 'ridge'
            w_rd, alp, l_rd, clf_rd = trainMulti(Xtr, KList, Ytr, mu=0, numintervals=numintervals, ldeltamin=ldeltamin,
                                            ldeltamax=ldeltamax, method='ridge', selectK=False, regression=False, SList=SList, UList=UList)

            y_pred_linear = predictMulti(Xte, SvList, UvList, l_linear, clf_linear)
            y_pred_lasso = predictMulti(Xte, SvList, UvList, l_lasso, clf_lasso)
            y_pred_rd = predictMulti(Xte, SvList, UvList, l_rd, clf_rd)

            m = []
            m.append(y_pred_linear)
            m.append(y_pred_lasso)
            m.append(y_pred_rd)
            m = np.array(m)
            if REML:
                np.savetxt('../results'+str(z)+'/EEGResult_REML_label_'+str(l+1)+'_con_'+str(4)+'.csv', m, delimiter=',')
            else:
                np.savetxt('../results'+str(z)+'/EEGResult_ML_label_'+str(l+1)+'_con_'+str(4)+'.csv', m, delimiter=',')



def runGenome(numintervals=100, ldeltamin=-5, ldeltamax=5):
    X, Y, Z1, Z2, B = GenLoading(True)
    for REML in [True, False]:
        for i in range(5):
            if i!=3:
                print 'Genome', i
                K, U, S = GenLoadingKSU(i)
                w_linear, alp, l_linear, clf_linear = train(X, K, Y, mu=0, numintervals=numintervals, ldeltamin=ldeltamin,
                                                            ldeltamax=ldeltamax, method='linear', selectK=True, regression=True, S=S, U=U, REML=REML)
                w_lasso, alp, l_lasso, clf_lasso = train(X, K, Y, mu=0, numintervals=numintervals, ldeltamin=ldeltamin,
                                                         ldeltamax=ldeltamax, method='lasso', selectK=True, regression=True, S=S, U=U, REML=REML)
                w_rd, alp, l_rd, clf_rd = train(X, K, Y, mu=0, numintervals=numintervals, ldeltamin=ldeltamin, ldeltamax=ldeltamax,
                                                method='ridge', selectK=True, regression=True, S=S, U=U, REML=REML)
                m = []
                m.append(w_linear)
                m.append(w_lasso)
                m.append(w_rd)
                m = np.array(m)
                if REML:
                    np.savetxt('../results/genomeResult_REML_con_'+str(i+1)+'.csv', m, delimiter=',')
                else:
                    np.savetxt('../results/genomeResult_ML_con_'+str(i+1)+'.csv', m, delimiter=',')

        print 'Genome 3'
        K0, U0, S0 = GenLoadingKSU(0)
        K1, U1, S1 = GenLoadingKSU(1)
        KList = [K0, K1]
        UList = [U0, U1]
        SList = [S0, S1]
        w_linear, alp, l_linear, clf_linear = trainMulti(X, KList, Y, mu=0, numintervals=numintervals, ldeltamin=ldeltamin,
                                                    ldeltamax=ldeltamax, method='linear', selectK=True, regression=True, SList=SList, UList=UList)
        w_lasso, alp, l_lasso, clf_lasso = trainMulti(X, KList, Y, mu=0, numintervals=numintervals, ldeltamin=ldeltamin,
                                                 ldeltamax=ldeltamax, method='lasso', selectK=True, regression=True, SList=SList, UList=UList)
        w_rd, alp, l_rd, clf_rd = trainMulti(X, KList, Y, mu=0, numintervals=numintervals, ldeltamin=ldeltamin, ldeltamax=ldeltamax,
                                        method='ridge', selectK=True, regression=True, SList=SList, UList=UList)
        m = []
        m.append(w_linear)
        m.append(w_lasso)
        m.append(w_rd)
        m = np.array(m)
        if REML:
            np.savetxt('../results/genomeResult_REML_con_'+str(4)+'.csv', m, delimiter=',')
        else:
            np.savetxt('../results/genomeResult_ML_con_'+str(4)+'.csv', m, delimiter=',')



def runRandomData(numintervals=100, ldeltamin=-5, ldeltamax=5):
    X, Y, Z1, Z2, B = RanLoading(True)
    for REML in [True, False]:
        for i in range(5):
            if i!=3:
                print 'RandomData', i
                K, U, S = RanLoadingKSU(i)
                w_linear, alp, l_linear, clf_linear = train(X, K, Y, mu=0, numintervals=numintervals, ldeltamin=ldeltamin,
                                                            ldeltamax=ldeltamax, method='linear', selectK=True, regression=True, S=S, U=U, REML=REML)
                w_lasso, alp, l_lasso, clf_lasso = train(X, K, Y, mu=0, numintervals=numintervals, ldeltamin=ldeltamin,
                                                         ldeltamax=ldeltamax, method='lasso', selectK=True, regression=True, S=S, U=U, REML=REML)
                w_rd, alp, l_rd, clf_rd = train(X, K, Y, mu=0, numintervals=numintervals, ldeltamin=ldeltamin, ldeltamax=ldeltamax,
                                                method='ridge', selectK=True, regression=True, S=S, U=U, REML=REML)
                m = []
                m.append(w_linear)
                m.append(w_lasso)
                m.append(w_rd)
                m = np.array(m)
                if REML:
                    np.savetxt('../results/RandomDataResult_REML_con_'+str(i+1)+'.csv', m, delimiter=',')
                else:
                    np.savetxt('../results/RandomDataResult_ML_con_'+str(i+1)+'.csv', m, delimiter=',')

        print 'Random 3'
        K0, U0, S0 = RanLoadingKSU(0)
        K1, U1, S1 = RanLoadingKSU(1)
        KList = [K0, K1]
        UList = [U0, U1]
        SList = [S0, S1]
        w_linear, alp, l_linear, clf_linear = trainMulti(X, KList, Y, mu=0, numintervals=numintervals, ldeltamin=ldeltamin,
                                                    ldeltamax=ldeltamax, method='linear', selectK=True, regression=True, SList=SList, UList=UList)
        w_lasso, alp, l_lasso, clf_lasso = trainMulti(X, KList, Y, mu=0, numintervals=numintervals, ldeltamin=ldeltamin,
                                                 ldeltamax=ldeltamax, method='lasso', selectK=True, regression=True, SList=SList, UList=UList)
        w_rd, alp, l_rd, clf_rd = trainMulti(X, KList, Y, mu=0, numintervals=numintervals, ldeltamin=ldeltamin, ldeltamax=ldeltamax,
                                        method='ridge', selectK=True, regression=True, SList=SList, UList=UList)
        m = []
        m.append(w_linear)
        m.append(w_lasso)
        m.append(w_rd)
        m = np.array(m)
        if REML:
            np.savetxt('../results/RandomDataResult_REML_con_'+str(4)+'.csv', m, delimiter=',')
        else:
            np.savetxt('../results/RandomDataResult_ML_con_'+str(4)+'.csv', m, delimiter=',')


if __name__ == '__main__':
    # runGenome(1000, -10, 10)
    # runEEG(1000, -10, 10, 2000, 2)
    # runEEG(1000, -10, 10, 4000, 4)
    # runEEG(1000, -10, 10, 6000, 6)
    # runEEG(1000, -10, 10, 8000, 8)
    # runEEG(1000, -10, 10, 10000, 0)
    runRandomData(1000, -10 , 10)
    # print '=================='
    # print 'GROUP 2'
    # print '=================='
    # runEEG(1000, -10, 10, 2000, 2)
    # print '=================='
    # print 'GROUP 4'
    # print '=================='
    # runEEG(1000, -10, 10, 4000, 4)
    # print '=================='
    # print 'GROUP 6'
    # print '=================='
    # runEEG(1000, -10, 10, 6000, 6)
    # print '=================='
    # print 'GROUP 8'
    # print '=================='
    # runEEG(1000, -10, 10, 8000, 8)
    # print '=================='
    # print 'GROUP 0'
    # print '=================='
    # runEEG(1000, -10, 10, 10000, 0)
    # print '=================='
    # print 'DONE'
    # print '=================='
