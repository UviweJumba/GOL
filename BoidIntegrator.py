import numpy as np
import pygame


class BoidIntegrator:

    

    def __init__(self, screen, x_star, N=5, M =5, k_sep=1, k_coh=1, k_align=1, col=(233, 10, 10)):
        self.rng = np.random.default_rng()
        self.N = N
        self.M = M
        self.range = 200
        self.color = col
        self.screen = screen
        

        self.k_sep = k_sep
        self.k_coh = k_coh
        self.k_align = k_align

        self.a_agr = 0.1
        self.a_tim = 0.001

        self.X = self.rng.random((N, 2))*100 + x_star
        self.X_dot = self.rng.standard_normal((N, 2))*10
        self.X_ddot = np.zeros((N, 2))

        self.X_mean = np.zeros((N, 2))
        self.V_mean = np.zeros((N, 2))

        self.speed_limit = 30

        self.Y = None


    def update(self, dt, x_star):

        A_align = np.zeros((self.N,2))
        A_coh = np.zeros((self.N,2))
        A_sep = np.zeros((self.N,2))

        self.X_mean = np.mean(self.X, axis=0)
        self.V_mean = np.mean(self.X_dot, axis=0)

        R_XX = self.X[:, np.newaxis, :] - self.X[np.newaxis, :, :]
        D_X = np.linalg.norm(R_XX, axis=2)
        np.fill_diagonal(D_X, 1e-5)

        R_Xdot = self.X_dot[:, np.newaxis] - self.X_dot[np.newaxis, :, :]
        
        Nx_mask = D_X < self.range
        N_x = np.sum(Nx_mask, axis=1)
        

        ## Flocking Mechanics
        A_sep = 10 * np.einsum("i,ij->ij", (1/np.sum(D_X.dot(D_X), axis=0) ), self.X - self.X_mean)
        A_coh = 1* self.k_coh * self.V_mean - self.X_dot
        A_align = 1* self.k_align * self.X_mean - self.X

        print("Acoh = ", A_coh)
        print("Aalign = ", A_align)

        if x_star is not None:
            A_fol = 0.5*(x_star - self.X)
        else:
            A_fol = 0

        self.X_ddot = A_fol + A_align + A_coh + A_sep

        # self.enforce_speed_limit()
       
        self.X, self.X_dot = self.EulerIntergrate(self.X, self.X_dot, self.X_ddot, dt)
        


    def EulerIntergrate(self, x, v, a, dt):
        v += a*dt
        x += v*dt

        # print(x)

        return (x,v)


    def draw(self):
        for x in self.X:
            pygame.draw.rect(self.screen, self.color, (x[0], x[1] , 10, 10))


    def flock(self, R_ij, V_ij, distances, neighbors):
        """
        Compute acceleration based on flocking dynamics: separation, alignment, and cohesion.

        Parameters:
        - X (ndarray): Position matrix of the flock of shape (N, 2).
        - X_dot (ndarray): Velocity matrix of the flock of shape (N, 2).

        Returns:
        - acceleration (ndarray): Acceleration matrix of shape (N, 2).
        """

        """ 
        # # Separation: Steer away from nearby boids
        # A_sep = np.zeros((distances.shape[0], 2))
        # mask_sep = distances < 50
        # A_sep = np.sum((R_ij/ (distances[..., np.newaxis]**2 + 1e-5)) * mask_sep, axis=1)
        

        # # Alignment: Steer towards the average heading of neighbors
        # A_align = np.zeros((distances.shape[0], 2))
        # mask_align = distances < 50
        # A_align = np.sum(V_ij*mask_align[...,np.newaxis], axis=1) / (neighbors + 1e-5)
        


        # # Cohesion: Steer towards the average position of neighbors
        # A_coh = np.zeros((distances.shape[0], 2))
        # mask_coh = distances < 50
        # A_coh = np.sum(R_ij*mask_coh[..., np.newaxis], axis=1) / (neighbors + 1e-5)
        """

        ## Seperation
        #A_sep = ( R_X/(R_X*R_X) ).transpose().dot(np.ones((5)) ).transpose()
        A_sep = self.k_sep * (1/neighbors).dot( np.sum(R_ij, axis=0) /(distances.transpose().dot(distances)) ) 
        # Y_sep = self.k_sep * (1/M_y).dot(np.ones((self.M)).transpose().dot( self.R_Y/(self.R_Y * self.R_Y) ) )

        ## Cohesion
        A_coh = self.k_coh * (1/neighbors).dot( np.ones((self.N)).transpose().dot( R_Xdot ) )
        # Y_coh = self.k_coh * (1/M_y).dot( np.ones((self.M)).transpose().dot( R_Ydot ) )
        

        ## Alignment
        A_align = self.k_align * (1/neighbors).dot( np.sum(R_ij) )
        # Y_align = self.k_align * (1/M_y).dot( R_yi )
        
        
        return A_sep + A_coh + A_align

    def enforce_speed_limit(self):
        U = 20*np.einsum( "i,ij->ij", ( 1/np.linalg.norm(self.X_dot, axis=1) ), self.X_dot )
        # print("U = ", U)
        self.X_dot[np.linalg.norm(self.X_dot, axis=1) < 200] = U

        

    def set_adversary_positions(self, P):
        self.Y = P


    def set_player_accel(self, v):
        self.X_ddot[self.lead_indx] = np.array(v)

    def elementwise_dot(self, V, M):
        print("M shape= ", M.shape)
        out = np.zeros(M.shape)
        for i in range(0, M.shape[1]):
            for j in range(0, M.shape[0]):
                out[i][j] = V[i].dot( M[i][j] )
                
        return out

    
    def get_relative_displacements(self, X, Y):
        out = np.zeros((len(X),  len(Y), 2))
        neighs = np.zeros((len(X)))

        for i in range(0, len(X)):
            count = 0
            for j in range(0, len(Y)):
                    if (X[i] - Y[j]).dot( X[i] - Y[j] ) <= 100:
                        count += 1

                    if (X[i] - Y[j]).any() <= 0.001:
                        out [i][j] = np.ones(2)*0.001
                    else:
                        out [i][j] = X[i] - Y[j]
            if count == 0:
                count = 1

            neighs[i] = count
        # print(out)
        return out, neighs


    def compute_theta(self, V, R_ij):
        """
        Compute the dot product of each velocity with the normalized relative displacement.

        Parameters:
        - V (ndarray): Velocity matrix of shape (N, 2).
        - R_ij (ndarray): Relative displacement tensor of shape (N, M, 2).

        Returns:
        - theta (ndarray): Dot product of each velocity with the normalized relative displacement.
        """
        # Normalize velocities
        V_normalized = V / (np.linalg.norm(V, axis=1, keepdims=True) + 1e-5)
        
        # Normalize the relative displacements
        distances = np.linalg.norm(R_ij, axis=2)
        R_ij_normalized = R_ij / (distances[..., np.newaxis] + 1e-5)

        
        # Compute theta
        theta = np.einsum('ij,ijk->ik', V_normalized, np.transpose(R_ij_normalized, (0,2,1)))
        
        return theta

    def shoot():
        ## All boids shoot
        Projs = Projectiles(self.X, self.X_dot)
        Projs.update()



