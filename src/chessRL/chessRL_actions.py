"""
@author: Octavio Bomfim Santiago
Created on 10/07/2020
"""

from keras.preprocessing.text import Tokenizer
import nltk
from nltk.tokenize import word_tokenize
import numpy as np
import re
from keras.utils import to_categorical
import pandas as pd
import pickle
from matplotlib import style
from collections import deque
import matplotlib.pyplot as plt

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Embedding
from keras.preprocessing.sequence import pad_sequences
from keras.optimizers import Adam
from keras import backend as K

import tensorflow as tf

import gym
import gym_chess
import random
import chess
import chess.engine
from gym_chess.alphazero import BoardEncoding

from difflib import SequenceMatcher



def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def act(cnt,df,seq_len, model, tokenizer, obs, legal_moves, engine, state, opening: str=None, idx_open: int=0, debug = False, choice = 2):
    #start
    if cnt == 0:
        if opening == None:
            #random opening
            idx = random.choice([x for x in range(0,len(df['moves']))])
            moves = df['moves'][idx].split()
            move = moves[0]
        else:
            moves = df[df['opening_name'] == opening]['moves'].iloc[idx_open].split()
            move = moves[0]
            
        return move

    else:
        if choice == 0:
            if opening != None:
                if (cnt <= int(df[df['opening_name'] == opening]['opening_ply'].iloc[idx_open])):
                    moves = df[df['opening_name'] == opening]['moves'].iloc[idx_open].split()
                    move = moves[cnt]
                    return move
                else:
                    for idx,line in enumerate(df[df['opening_name'] == opening]['moves']):
                        op_idx = int(df[df['opening_name'] == opening]['opening_ply'].iloc[idx])
                        moves = line.split()[cnt:]
                        if len(moves) >= 3:
                            move = moves[2]
                            #print("teste: ", move)
                            if move in legal_moves:
                                print("teste certo: ", move)
                                return move
                        else:
                            return legal_moves[0]
   
        elif choice == 1:
            df2 = df.copy()
            df2['similarities'] = df2['moves'].apply(lambda x: similar(x.split(), obs))
            df2 = df2.sort_values(by=['similarities'], ascending = False)
            #moves = moves[cnt-1:]
            for i in range(0,len(df2['moves'])):
                moves = df2['moves'][i].split()
                if debug:
                    print("Similarity of , ", df2['similarities'][i] * 100, "%")
                    print(obs[-1])
                if obs[-1] in moves:
                    try:
                        if debug:
                            #similarity
                            print("Next move: ",moves[moves.index(obs[-1]) + 1])
                            print("game: ",moves[moves.index(obs[-1])-2:moves.index(obs[-1])+2])
                        move = moves[moves.index(obs[-1]) + 1]
                        if move in legal_moves:
                            break
                    except:
                        #ML predict
                        #print("Machine Learning")
                        board = ' '.join([str(elem) for elem in obs])
                        next_moves = predict(seq_len,model, tokenizer, board)
                        move = next_moves
                        move = [x.capitalize() if len(x) > 2 else x for x in move]
                        for i in move:
                            if i in legal_moves:
                                move = i
                                break
                else:
                    #ML predict
                    #print("Machine Learning")
                    board = ' '.join([str(elem) for elem in obs])
                    next_moves = predict(seq_len,model, tokenizer, board)
                    move = next_moves
                    move = [x.capitalize() if len(x) > 2 else x for x in move]
                    for i in move:
                        if i in legal_moves:
                            move = i
                            return move
                        
                    move = random.choice(legal_moves)
                    return move
                        

        elif choice == 2:
            result = engine.play(state, chess.engine.Limit(time=0.1))
            move = state.san(result.move)
            return move
