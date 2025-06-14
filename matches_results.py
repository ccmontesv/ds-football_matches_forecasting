import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.stats import poisson,skellam
from scipy.optimize import minimize
import os
from datetime import datetime 

pd.options.mode.chained_assignment = None  # Suppress SettingWithCopyWarning

def matches_results(league,fl_web_csv_1,fl_web_csv_2,df_matches):
    
    from datetime import datetime

    # read and clean CSV files
    n = np.linspace(1, 190, 190)
    fl = pd.read_csv(fl_web_csv_1, skiprows=n)
    fl = fl[['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'Date','HST','AST']]  # add the date column
    fl = fl.rename(columns={'FTHG': 'HomeGoals', 'FTAG': 'AwayGoals'})

    fl_new = pd.read_csv(fl_web_csv_2)
    fl_new = fl_new[['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'Date','HST','AST']]
    fl_new = fl_new.rename(columns={'FTHG': 'HomeGoals', 'FTAG': 'AwayGoals'})

    fl = pd.concat([fl,fl_new])
    fl.index = range(fl.shape[0])

    #---------------------------------------------
    fl['Date'] = pd.to_datetime(fl['Date'], format='%d/%m/%Y')  # Ajusta el formato de fecha si es necesario

    # time decayment parameter
    decay_factor = 0.95  # the closer the parameter, the lower the time impact the outcome

    today = datetime.today()
    fl['days_since'] = (today - fl['Date']).dt.days

    # time weights calculation
    fl['weight'] = decay_factor ** (fl['days_since'] / 30)  #monthly based weighting
    #----------------------------------------------
    
    
    #THIS PART FINDS THE PARAMETERS
    def rho_correction(x, y, lambda_x, mu_y, rho):
        if x==0 and y==0:
            return 1- (lambda_x * mu_y * rho)
        elif x==0 and y==1:
            return 1 + (lambda_x * rho)
        elif x==1 and y==0:
            return 1 + (mu_y * rho)
        elif x==1 and y==1:
            return 1 - rho
        else:
            return 1.0

    def solve_parameters(dataset, debug = False, init_vals=None, options={'disp': True, 'maxiter':100},
                         constraints = [{'type':'eq', 'fun': lambda x: sum(x[:20])-20}] , **kwargs):
        
        teams = np.sort(dataset['HomeTeam'].unique())

        # check for no weirdness in dataset
        away_teams = np.sort(dataset['AwayTeam'].unique())
        n_teams = len(teams)
        
        if init_vals is None:
            # random initialisation of model parameters
            init_vals = np.concatenate((np.random.uniform(0,1,(n_teams)), # attack strength
                                          np.random.uniform(0,-1,(n_teams)), # defence strength
                                          np.array([0, 1.0]) # rho (score correction), gamma (home advantage)
                                         ))
            
        # Función de log-verosimilitud ponderada
        def weighted_log_like(x, y, alpha_x, beta_x, alpha_y, beta_y, rho, gamma, weight):
            lambda_x, mu_y = np.exp(alpha_x + beta_y + gamma), np.exp(alpha_y + beta_x)
            return weight * (np.log(rho_correction(x, y, lambda_x, mu_y, rho)) +
                             np.log(poisson.pmf(x, lambda_x)) + np.log(poisson.pmf(y, mu_y)))

        def estimate_parameters(params):
            score_coefs = dict(zip(teams, params[:n_teams]))
            defend_coefs = dict(zip(teams, params[n_teams:(2*n_teams)]))
            rho, gamma = params[-2:]
            
            log_like = [weighted_log_like(row.HomeGoals, row.AwayGoals, score_coefs[row.HomeTeam], defend_coefs[row.HomeTeam],
                score_coefs[row.AwayTeam], defend_coefs[row.AwayTeam], rho, gamma, row.weight) for row in dataset.itertuples()]
            return -sum(log_like)
        
        opt_output = minimize(estimate_parameters, init_vals, options=options, constraints = constraints, **kwargs)
        
        if debug:
            # sort of hacky way to investigate the output of the optimisation process
            return opt_output
        else:
            return dict(zip(["attack_"+team for team in teams] + 
                            ["defence_"+team for team in teams] +
                            ['rho', 'home_adv'],
                            opt_output.x))
        
    params = solve_parameters(fl)
    
    #THIS PART APPLIES THE PARAMETERS TO THE CURRENT MATCHES

    def calc_means(param_dict, homeTeam, awayTeam):
        return [np.exp(param_dict['attack_'+homeTeam] + param_dict['defence_'+awayTeam] + param_dict['home_adv']),
                    np.exp(param_dict['defence_'+homeTeam] + param_dict['attack_'+awayTeam])]

    def dixon_coles_simulate_match(params_dict, homeTeam, awayTeam, max_goals=10):
        team_avgs = calc_means(params_dict, homeTeam, awayTeam)
        team_pred = [[poisson.pmf(i, team_avg) for i in range(0, max_goals+1)] for team_avg in team_avgs]
        output_matrix = np.outer(np.array(team_pred[0]), np.array(team_pred[1]))
        correction_matrix = np.array([[rho_correction(home_goals, away_goals, team_avgs[0],
                                                           team_avgs[1], params['rho']) for away_goals in range(2)]
                                           for home_goals in range(2)])
        output_matrix[:2,:2] = output_matrix[:2,:2] * correction_matrix
        return output_matrix

    #--------------------------------------------------------

    def get_avg_shots_on_target(fl, team, last_n_matches=5):
        # Filter matches where the team played (home or away)
        team_matches = fl[(fl['HomeTeam'] == team) | (fl['AwayTeam'] == team)].copy()

        # Sort matches by date (most recent first)
        team_matches = team_matches.sort_values(by='Date', ascending=False)

        # Select the last `last_n_matches`
        last_matches = team_matches.head(last_n_matches)

        # Calculate shots on target for those matches (using .loc to avoid SettingWithCopyWarning)
        last_matches.loc[:, 'SoT'] = last_matches.apply(
            lambda row: row['HST'] if row['HomeTeam'] == team else row['AST'],
            axis=1
        )

        # Return the average
        return last_matches['SoT'].mean()


#--------------- PREDICTING THE MATCHES OUTCOMES------------------
    
    now = datetime.now()

    # Format the output to include date and hour
    current_time = now.strftime("%Y-%m-%d %H")
    
    file = open(f"Results_{current_time}.txt", "a")
    
    m = df_matches    #m originally was designated as df_matches dataframe
    #print(m)
   
    n_matchs = len(m.index) #number of matches 
    g = 10;   #goals to take into account
    
    print('*** ' + league + ' ***')
    print('')
    
    file.write('')
    file.write('   ' + current_time + os.linesep)
    file.write('*** ' + league + ' ***' + os.linesep + os.linesep)

    for i in range(n_matchs):
                
        ht = m.iloc[i,0]
        at = m.iloc[i,1]
        match =  dixon_coles_simulate_match(params, ht, at, g)  #matrix with match-score results

        M=match

        d = np.trace(match)*100;        #draw

        s=0
        for i in range(1,g):
            for j in range(0,i):
                s=s+M[i][j]
                #print (M[i][j])
        hw=s*100;                      #home win

        s=0
        for i in range(0,g):
            for j in range(i+1,g):
                s=s+M[i][j]
                #print (M[i][j])
        aw=s*100;                      #away win
        
        hw = "{:.2f}".format(hw)
        d =  "{:.2f}".format(d)
        aw = "{:.2f}".format(aw)

        # Calculate average shots on target for both teams
        ht_avg_shots = get_avg_shots_on_target(fl, ht)
        at_avg_shots = get_avg_shots_on_target(fl, at)
        diff_tiros = abs(ht_avg_shots-at_avg_shots)
        
        print(f"{ht}: {hw},       st: {ht_avg_shots:.1f}")
        print(f"{at}: {aw},       st: {at_avg_shots:.1f}")
        print(f"Draw: {d},        diff: {diff_tiros:.1f} \n")

        # Write to file
        file.write(f"{ht}: {hw}%,     Avg Shots: {ht_avg_shots:.1f}{os.linesep}")
        file.write(f"{at}: {aw}%,     Avg Shots: {at_avg_shots:.1f}{os.linesep}")
        file.write(f"Draw: {d}%{os.linesep}\n")

    file.close()