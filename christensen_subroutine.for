C Start of Base code, DO NOT change

C---------------------------------------------------------------------------------------
      SUBROUTINE UMAT(STRESS,STATEV,DDSDDE,SSE,SPD,SCD,
     1 RPL,DDSDDT,DRPLDE,DRPLDT,
     2 STRAN,DSTRAN,TIME,DTIME,TEMP,DTEMP,PREDEF,DPRED,CMNAME,
     3 NDI,NSHR,NTENS,NSTATV,PROPS,NPROPS,COORDS,DROT,PNEWDT,
     4 CELENT,DFGRD0,DFGRD1,NOEL,NPT,LAYER,KSPT,JSTEP,KINC)
C

      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME
      DIMENSION STRESS(NTENS),STATEV(NSTATV),
     1 DDSDDE(NTENS,NTENS),DDSDDT(NTENS),DRPLDE(NTENS),
     2 STRAN(NTENS),DSTRAN(NTENS),TIME(2),PREDEF(1),DPRED(1),
     3 PROPS(NPROPS),COORDS(3),DROT(3,3),DFGRD0(3,3),DFGRD1(3,3),
     4 JSTEP(4),PS(3)
C---------------------------------------------------------------------------------------

C End of Base code

C---------------------------------------------------------------------------------------
C---------------------------------------------------------------------------------------

C Start of USER code

C---------------------------------------------------------------------------------------
C           PROPS(NPROPS)
C           User-specified array of material constants associated with this user material.
C
C           NPROPS
C           User-defined number of material constants associated with this user material.
C
C           PROPS(1) = Elasticity Modulus
C           PROPS(2) = Poisson's Ratio
C           G = Shear Modulus
C           T = Tensile Strength
C           C = Compression Strength 

      PARAMETER (ONE = 1.0D0, TWO = 2.0D0)
      E = PROPS(1)
      v = PROPS(2)
      T = PROPS(3)
      C = PROPS(4) 
      G=E/(TWO*(ONE+v))

C           DDSDDE(NTENS,NTENS)
C           Jacobian matrix of the constitutive model

C           NTENS
C           Size of the stress or strain component array (NDI + NSHR).

C           NDI
C           Number of direct stress components at this point.

C           NSHR
C           Number of engineering shear stress components at this point.

C           Definition of the DDSDDE Jakobian Matrix for isotropic linear elastic materials
       
      DO i=1, NTENS
          DO j=1, NTENS
              DDSDDE(j, i)=0.0D0
          END DO
      END DO
      

      DDSDDE(1, 1) = (E*(ONE-v))/((ONE+v)*(ONE-TWO*v))
      DDSDDE(2, 2) = (E*(ONE-v))/((ONE+v)*(ONE-TWO*v))
      DDSDDE(3, 3) = (E*(ONE-v))/((ONE+v)*(ONE-TWO*v))

      DDSDDE(1, 2) = (E*v)/((ONE+v)*(ONE-TWO*v))
      DDSDDE(1, 3) = (E*v)/((ONE+v)*(ONE-TWO*v))
      DDSDDE(2, 1) = (E*v)/((ONE+v)*(ONE-TWO*v))
      DDSDDE(2, 3) = (E*v)/((ONE+v)*(ONE-TWO*v))
      DDSDDE(3, 1) = (E*v)/((ONE+v)*(ONE-TWO*v))
      DDSDDE(3, 2) = (E*v)/((ONE+v)*(ONE-TWO*v))

      DDSDDE(4, 4) = G
      DDSDDE(5, 5) = G
      DDSDDE(6, 6) = G

      DO i=NDI+1, NTENS
          DDSDDE(i, i)=G
      END DO

C           Calculation of STRESSES 
C
C           STRESS(NTENS)
C           This array is passed in as the stress tensor at the beginning of the increment and must be updated
C           in this routine to be the stress tensor at the end of the increment.
C      
C           DSTRAN(NTENS)
C           Array of strain increments.

      DO i=1, NTENS
      DO j=1, NTENS
          STRESS(j)=STRESS(j)+DDSDDE(j, i)*DSTRAN(i)
      END DO
      END DO

C ----------------------------------------------------------------------------------
C      
C     IMPLEMENTATION OF THE FAILURE CRITERION IN  5 STEPS:
C
C     1. Calculate the principal stresses of the Stress tensor
C
C     2. Calculate the polar coordinates of the principal stresses
C
C     3. Calculate the failure index according to the invariants criterion
C
C     4. Calculate the failure index according to the fracture criterion (if needed)
C
C     5. Calculate the maximal failure index and print it as STATEV(1) 
C
C-----------------------------------------------------------------------------------

C     1. Calculate the principal stresses with the utility routine SPRINC
      CALL SPRINC(STRESS, PS, 1, 3, 3)


C     2. Calculate the polar coordinates of the principal stresses
      RHO=SQRT(PS(1)*PS(1) + PS(2)*PS(2) + PS(3)*PS(3))
      THETA=ATAN(SQRT(PS(1)*PS(1) + PS(2)*PS(2)),PS(3))
      PHI=ATAN(PS(2),PS(1))

      SIN_T=SIN(THETA)
      COS_T=COS(THETA)
      SIN_P=SIN(PHI)
      COS_P=COS(PHI)

C     3. Calculate the utility according to the invariants criterion
      AUX_A=1/(TWO*T*C) * ((SIN_T*COS_P-SIN_T*SIN_P) * (SIN_T*COS_P-SIN_T*SIN_P) +
     2 (SIN_T*COS_P-COS_T) * (SIN_T*COS_P-COS_T)+(SIN_T*SIN_P-COS_T)*(SIN_T*SIN_P-COS_T))
      AUX_B=(1/T-1/C)*(SIN_T*SIN_P+SIN_T*COS_P+COS_T)
      AUX_C=-ONE

      IF (AUX_A > 1.0D-10) THEN
            RHO_1 = ABS((-AUX_B+SQRT(AUX_B*AUX_B - 4*AUX_A*AUX_C)) / (2*AUX_A))
            RHO_2 = ABS((-AUX_B-SQRT(AUX_B*AUX_B - 4*AUX_A*AUX_C)) / (2*AUX_A))
            
            IF ((PS(1)+PS(2)+PS(3))>0) THEN
                  RHO_INV = MIN(RHO_1,RHO_2)
            ELSE
                  RHO_INV = MAX(RHO_1,RHO_2)
            END IF
      ELSE
            IF ((PS(1)+PS(2)+PS(3))>0) THEN
                  IF (AUX_B /= 0) THEN
                        RHO_INV = -AUX_C/AUX_B
                  ELSE
                        RHO_INV = 0.001
                  END IF
            ELSE
                  RHO_INV = 100
            END IF
      END IF

      UTIL_INV = RHO/RHO_INV

C     4. Calculate the utility according to the fracture criterion (if needed)
      UTIL_FRAC = MAX(PS(1), PS(2), PS(3))/T


C     5. Calculate the maximal utility and print it as STATEV(1)
      IF (T/C < 0.5) THEN
            UTIL = MAX(UTIL_INV, UTIL_FRAC)
      ELSE
            UTIL = UTIL_INV
      END IF
      
      
C     ---------------------      
c     FN as a FieldVariable
C     ---------------------

C     Calculate the karthesic coordinates from the utilization and the angles
      RHO_FAIL = RHO/UTIL
      PS_f_1 = RHO_FAIL * SIN(THETA) * COS(PHI)
      PS_f_2 = RHO_FAIL * SIN(THETA) * SIN(PHI)
      PS_f_3 = RHO_FAIL * COS(THETA)


C     Calculate the Failure number
      FN = 0.5 * ((3*T/C)-((PS_f_1+PS_f_2+PS_f_3)/C))

C     Fit the Failure number inside of its borders
      IF (FN < 0.) THEN
            FN = 0.
      ELSE IF (FN > 1.) THEN
            FN = 1.
      END IF

      
      STATEV(1) = UTIL
      STATEV(2) = FN
C---------------------------------------------------------------------------------------

C End of USER code

C---------------------------------------------------------------------------------------
      RETURN
      END