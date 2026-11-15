#!/usr/bin/env python3
"""
08_build_question_bank.py
-------------------------
Builds 05_Diagnostic_Application/Question_Bank/physics_question_bank_v1.json.

Every item is ORIGINAL, written in CBSE style. No CBSE previous-year question
text and no MTG content is reproduced: the bank exists so the diagnostic engine
has something to measure with, not to redistribute copyrighted material.
Each item carries its own answer, solution and (for written items) a rubric.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = (ROOT / "CBSE_Physics_2027_ROI_Project" / "05_Diagnostic_Application" /
       "Question_Bank" / "physics_question_bank_v1.json")

CH = {
    1: "Electric Charges and Fields",
    2: "Electrostatic Potential and Capacitance",
    3: "Current Electricity",
    4: "Moving Charges and Magnetism",
    5: "Magnetism and Matter",
    6: "Electromagnetic Induction",
    7: "Alternating Current",
    8: "Electromagnetic Waves",
    9: "Ray Optics and Optical Instruments",
    10: "Wave Optics",
    11: "Dual Nature of Radiation and Matter",
    12: "Atoms",
    13: "Nuclei",
    14: "Semiconductor Electronics: Materials, Devices and Simple Circuits",
}

AR_OPTIONS = [
    "Both A and R are true and R is the correct explanation of A",
    "Both A and R are true but R is not the correct explanation of A",
    "A is true but R is false",
    "Both A and R are false",
]

# (chapter, format, marks, difficulty, question, options, answer_index, answer_text, solution, rubric)
BANK = [
    # ---------------- Chapter 1
    (1, "MCQ", 1, 1, "Two point charges are separated by a distance d. If the separation is reduced to d/2, the electrostatic force between them becomes",
     ["one-fourth", "one-half", "twice", "four times"], 3, "four times",
     "Coulomb force varies as 1/d^2; halving d multiplies the force by 4.", None),
    (1, "MCQ", 1, 1, "The total electric flux through a closed surface enclosing a net charge q is",
     ["q times epsilon0", "q", "q divided by epsilon0", "zero"], 2, "q divided by epsilon0",
     "Gauss's theorem: total flux = enclosed charge / epsilon0.", None),
    (1, "MCQ", 1, 2, "The electric field at a point inside a uniformly charged thin spherical shell is",
     ["zero", "uniform and non-zero", "proportional to distance from centre", "infinite"], 0, "zero",
     "Field inside a uniformly charged thin shell is zero by Gauss's theorem.", None),
    (1, "MCQ", 1, 1, "The SI unit of electric dipole moment is",
     ["C m", "C m^-1", "C m^-2", "N C^-1"], 0, "C m",
     "Dipole moment p = q x 2a, charge times length, so coulomb metre.", None),
    (1, "AR", 1, 2, "Assertion (A): Electric field lines never intersect each other. Reason (R): The electric field at a point has a unique direction.",
     AR_OPTIONS, 0, "Both true, R explains A",
     "If lines crossed, the field would have two directions at one point, which is impossible.", None),
    (1, "SA", 2, 2, "Two charges +4 microcoulomb and -4 microcoulomb are separated by 0.20 m. Calculate the electric dipole moment of the pair.",
     None, None, "8 x 10^-7 C m",
     "p = q x 2a = 4 x 10^-6 C x 0.20 m = 8 x 10^-7 C m, directed from the negative to the positive charge.",
     "1 mark for the formula and substitution, 1 mark for the correct value with unit and direction."),

    # ---------------- Chapter 2
    (2, "MCQ", 1, 1, "The work done in moving a charge on an equipotential surface is",
     ["infinite", "zero", "equal to the potential", "proportional to the distance moved"], 1, "zero",
     "Work = q x potential difference, and the difference is zero on an equipotential surface.", None),
    (2, "MCQ", 1, 1, "A dielectric slab of dielectric constant K completely fills a parallel plate capacitor. Its capacitance becomes",
     ["K times", "K^2 times", "1/K times", "unchanged"], 0, "K times",
     "C = K epsilon0 A / d.", None),
    (2, "MCQ", 1, 2, "The energy stored in a 2 microfarad capacitor charged to 100 V is",
     ["0.001 J", "0.01 J", "0.1 J", "1 J"], 1, "0.01 J",
     "U = (1/2) C V^2 = 0.5 x 2e-6 x 10^4 = 0.01 J.", None),
    (2, "MCQ", 1, 2, "Three capacitors of 2, 3 and 6 microfarad are connected in series. The equivalent capacitance is",
     ["11 microfarad", "1 microfarad", "6 microfarad", "0.5 microfarad"], 1, "1 microfarad",
     "1/C = 1/2 + 1/3 + 1/6 = 1, so C = 1 microfarad.", None),
    (2, "AR", 1, 2, "Assertion (A): A conductor in electrostatic equilibrium is an equipotential volume. Reason (R): The electric field inside a conductor in electrostatic equilibrium is zero.",
     AR_OPTIONS, 0, "Both true, R explains A",
     "Zero internal field implies no potential difference between any two internal points.", None),
    (2, "SA", 2, 2, "A parallel plate capacitor of capacitance 10 microfarad is charged to 200 V and then disconnected. Calculate the energy stored and the energy if the separation is doubled at constant charge.",
     None, None, "0.20 J initially; 0.40 J after doubling",
     "U = Q^2/2C with Q = 2000 microcoulomb. Initially U = 0.20 J. Doubling the separation halves C, so U doubles to 0.40 J.",
     "1 mark for initial energy, 1 mark for the doubling argument and final value."),

    # ---------------- Chapter 3
    (3, "MCQ", 1, 1, "For a metallic conductor of fixed dimensions, doubling the current doubles the",
     ["number density of electrons", "drift velocity", "relaxation time", "resistivity"], 1, "drift velocity",
     "I = n A e v_d; n, A and e are fixed, so v_d doubles.", None),
    (3, "MCQ", 1, 2, "A wire is stretched so that its length doubles while its volume stays constant. Its resistance becomes",
     ["twice", "half", "four times", "unchanged"], 2, "four times",
     "R = rho L/A; with volume constant, A halves when L doubles, so R becomes 4 times.", None),
    (3, "MCQ", 1, 1, "Kirchhoff's junction rule is a statement of the conservation of",
     ["charge", "energy", "momentum", "mass"], 0, "charge", "Total current entering equals total current leaving a junction.", None),
    (3, "MCQ", 1, 2, "A cell of emf 2 V and internal resistance 0.5 ohm is connected to a 1.5 ohm resistor. The current is",
     ["0.5 A", "1 A", "1.33 A", "4 A"], 1, "1 A", "I = emf / (R + r) = 2 / 2 = 1 A.", None),
    (3, "AR", 1, 2, "Assertion (A): The terminal voltage of a cell is less than its emf when it is delivering current. Reason (R): There is a potential drop across the internal resistance of the cell.",
     AR_OPTIONS, 0, "Both true, R explains A", "V = emf - I r.", None),
    (3, "SA", 2, 2, "Two resistors of 3 ohm and 6 ohm are connected in parallel across a 6 V battery of negligible internal resistance. Find the total current drawn.",
     None, None, "3 A", "Equivalent resistance = 2 ohm; I = V/R = 6/2 = 3 A, or 2 A + 1 A branchwise.",
     "1 mark for the equivalent resistance or branch currents, 1 mark for the total current."),

    # ---------------- Chapter 4
    (4, "MCQ", 1, 1, "A charged particle moves parallel to a uniform magnetic field. The magnetic force on it is",
     ["maximum", "zero", "qvB", "along the field"], 1, "zero", "F = qvB sin(theta) with theta = 0.", None),
    (4, "MCQ", 1, 1, "The radius of the circular path of a charged particle in a uniform magnetic field is proportional to",
     ["momentum", "charge", "magnetic field", "charge squared"], 0, "momentum", "r = mv/(qB) = p/(qB).", None),
    (4, "MCQ", 1, 2, "A galvanometer is converted into an ammeter by connecting",
     ["a high resistance in series", "a low resistance in parallel", "a low resistance in series", "a capacitor in parallel"], 1, "a low resistance in parallel",
     "A shunt bypasses most of the current, lowering the effective resistance.", None),
    (4, "MCQ", 1, 2, "The magnetic field at the centre of a circular loop of radius r carrying current I is",
     ["mu0 I / (2r)", "mu0 I / (4 pi r)", "mu0 I r", "mu0 I / (2 pi r)"], 0, "mu0 I / (2r)",
     "Standard result from the Biot-Savart law.", None),
    (4, "AR", 1, 2, "Assertion (A): A current-carrying solenoid behaves like a bar magnet. Reason (R): The magnetic field lines of a solenoid closely resemble those of a bar magnet.",
     AR_OPTIONS, 0, "Both true, R explains A", "The pattern of field lines is the physical reason for the equivalence.", None),
    (4, "SA", 2, 2, "A straight wire of length 0.50 m carrying a current of 2.0 A lies perpendicular to a uniform magnetic field of 0.40 T. Calculate the force on the wire.",
     None, None, "0.40 N", "F = B I L sin(90) = 0.40 x 2.0 x 0.50 = 0.40 N.",
     "1 mark for the formula, 1 mark for the value with unit."),

    # ---------------- Chapter 5
    (5, "MCQ", 1, 1, "A material has relative permeability 900. It is",
     ["diamagnetic", "paramagnetic", "ferromagnetic", "non-magnetic"], 2, "ferromagnetic",
     "Relative permeability much greater than 1 indicates a ferromagnetic material.", None),
    (5, "MCQ", 1, 1, "A diamagnetic substance placed in a non-uniform magnetic field moves",
     ["towards the stronger field", "towards the weaker field", "along the field", "not at all"], 1, "towards the weaker field",
     "Diamagnetic materials are weakly repelled by a magnet.", None),
    (5, "MCQ", 1, 2, "The SI unit of magnetisation M is",
     ["A m^-1", "A m", "T", "A m^2"], 0, "A m^-1", "Magnetisation is magnetic moment per unit volume.", None),
    (5, "MCQ", 1, 2, "For a paramagnetic material, the magnetic susceptibility varies with absolute temperature T as",
     ["T", "T^2", "1/T", "independent of T"], 2, "1/T", "Curie law: susceptibility is proportional to 1/T.", None),
    (5, "AR", 1, 2, "Assertion (A): Magnetic field lines form closed loops. Reason (R): Magnetic monopoles do not exist.",
     AR_OPTIONS, 0, "Both true, R explains A", "Gauss's law for magnetism gives zero net flux through any closed surface.", None),
    (5, "SA", 2, 2, "A bar magnet of magnetic moment 0.50 A m^2 is placed in a uniform magnetic field of 0.20 T with its axis at 30 degrees to the field. Calculate the torque on it.",
     None, None, "0.050 N m", "Torque = m B sin(theta) = 0.50 x 0.20 x 0.50 = 0.050 N m.",
     "1 mark for the formula, 1 mark for substitution and value."),

    # ---------------- Chapter 6
    (6, "MCQ", 1, 1, "Lenz's law is a consequence of the conservation of",
     ["charge", "momentum", "energy", "mass"], 2, "energy", "The induced current opposes the change that produced it, so no energy is created.", None),
    (6, "MCQ", 1, 2, "A coil of 100 turns experiences a change of flux of 0.020 Wb in 0.10 s. The average induced emf is",
     ["0.2 V", "2 V", "20 V", "200 V"], 2, "20 V", "emf = N dPhi/dt = 100 x 0.020/0.10 = 20 V.", None),
    (6, "MCQ", 1, 1, "The SI unit of self-inductance expressed in base terms is",
     ["V s A^-1", "V A^-1 s^-1", "V s^-1 A", "V A s"], 0, "V s A^-1", "Henry = volt second per ampere.", None),
    (6, "MCQ", 1, 2, "Mutual inductance between two coils depends on",
     ["current in the primary only", "geometry and relative orientation of the coils", "resistance of the coils", "the emf applied"], 1, "geometry and relative orientation",
     "M is purely geometric for a given medium.", None),
    (6, "AR", 1, 2, "Assertion (A): The induced emf in a coil is zero when the magnetic flux through it is constant. Reason (R): Induced emf depends on the rate of change of magnetic flux.",
     AR_OPTIONS, 0, "Both true, R explains A", "Faraday's law: emf = -dPhi/dt.", None),
    (6, "SA", 2, 2, "A rectangular loop of area 0.10 m^2 lies perpendicular to a uniform magnetic field of 0.50 T. It is turned parallel to the field in 0.10 s. Find the average induced emf.",
     None, None, "0.50 V", "Initial flux 0.050 Wb, final flux 0; emf = 0.050/0.10 = 0.50 V.",
     "1 mark for initial and final flux, 1 mark for the emf value."),

    # ---------------- Chapter 7
    (7, "MCQ", 1, 1, "The rms value of a sinusoidal alternating current of peak value I0 is",
     ["I0", "I0/2", "I0/sqrt(2)", "2 I0"], 2, "I0/sqrt(2)", "Standard result for a sine wave.", None),
    (7, "MCQ", 1, 2, "In a series LCR circuit at resonance, the impedance is",
     ["maximum and equal to XL", "minimum and equal to R", "zero", "equal to XC"], 1, "minimum and equal to R",
     "XL = XC, so the reactances cancel and Z = R.", None),
    (7, "MCQ", 1, 2, "The power factor of a circuit in which the current and voltage differ in phase by 90 degrees is",
     ["1", "0.5", "zero", "0.707"], 2, "zero", "Power factor = cos(90) = 0; the current is wattless.", None),
    (7, "MCQ", 1, 1, "In a step-down transformer",
     ["N secondary is greater than N primary", "N secondary is less than N primary", "the frequency changes", "the power increases"], 1, "N secondary is less than N primary",
     "Vs/Vp = Ns/Np, so a lower secondary voltage needs fewer secondary turns.", None),
    (7, "AR", 1, 2, "Assertion (A): In a series LCR circuit at resonance the current is maximum. Reason (R): At resonance the inductive and capacitive reactances cancel, leaving only the resistance.",
     AR_OPTIONS, 0, "Both true, R explains A", "Minimum impedance gives maximum current.", None),
    (7, "SA", 2, 2, "An alternating voltage has an rms value of 220 V at 50 Hz. Write its instantaneous voltage equation and state the peak value.",
     None, None, "V = 311 sin(314 t) volt; peak 311 V",
     "Peak = 220 x sqrt(2) = 311 V; angular frequency = 2 pi x 50 = 314 rad/s.",
     "1 mark for the peak value, 1 mark for the correct equation."),

    # ---------------- Chapter 8
    (8, "MCQ", 1, 1, "In an electromagnetic wave, the electric field, the magnetic field and the direction of propagation are",
     ["all parallel", "mutually perpendicular", "E and B parallel, propagation perpendicular", "randomly oriented"], 1, "mutually perpendicular",
     "EM waves are transverse.", None),
    (8, "MCQ", 1, 2, "Displacement current arises in a region where",
     ["the magnetic field is constant", "the electric field is changing with time", "there is a steady current", "there is no field"], 1, "the electric field is changing with time",
     "Id = epsilon0 dPhiE/dt.", None),
    (8, "MCQ", 1, 1, "Which of these electromagnetic waves has the shortest wavelength?",
     ["microwaves", "infrared", "ultraviolet", "gamma rays"], 3, "gamma rays", "Gamma rays lie at the short-wavelength end of the spectrum.", None),
    (8, "MCQ", 1, 2, "The speed of an electromagnetic wave in a medium of permittivity epsilon and permeability mu is",
     ["sqrt(mu epsilon)", "1/sqrt(mu epsilon)", "mu epsilon", "1/(mu epsilon)"], 1, "1/sqrt(mu epsilon)",
     "c = 1/sqrt(mu0 epsilon0) in vacuum, generalised to the medium.", None),
    (8, "AR", 1, 2, "Assertion (A): A changing electric field can produce a magnetic field. Reason (R): Displacement current behaves like a conduction current in producing a magnetic field.",
     AR_OPTIONS, 0, "Both true, R explains A", "Maxwell's displacement current completes Ampere's circuit law.", None),
    (8, "SA", 2, 2, "An electromagnetic wave has a frequency of 30 MHz. Calculate its wavelength in vacuum and identify the region of the electromagnetic spectrum.",
     None, None, "10 m; radio waves", "lambda = c/nu = 3e8 / 3e7 = 10 m, which is in the radio region.",
     "1 mark for wavelength, 1 mark for identifying radio waves."),

    # ---------------- Chapter 9
    (9, "MCQ", 1, 1, "An object is placed at the centre of curvature of a concave mirror. The image is",
     ["at infinity", "at the centre of curvature, real and inverted", "at the focus", "virtual and erect"], 1, "at the centre of curvature, real and inverted",
     "At u = 2f, v = 2f with magnification -1.", None),
    (9, "MCQ", 1, 2, "The critical angle for a glass-air interface of refractive index 1.50 is closest to",
     ["24 degrees", "42 degrees", "49 degrees", "60 degrees"], 1, "42 degrees", "sin C = 1/1.5 = 0.667, C = 41.8 degrees.", None),
    (9, "MCQ", 1, 1, "The power of a convex lens of focal length 20 cm is",
     ["+5 D", "+0.05 D", "-5 D", "+20 D"], 0, "+5 D", "P = 1/f with f in metres = 1/0.20 = +5 D.", None),
    (9, "MCQ", 1, 2, "The magnifying power of an astronomical telescope for a relaxed eye is",
     ["fe/fo", "fo/fe", "fo x fe", "1 + D/fe"], 1, "fo/fe", "M = fo/fe with the final image at infinity.", None),
    (9, "AR", 1, 2, "Assertion (A): A convex lens can behave as a diverging lens when placed in a medium of higher refractive index. Reason (R): The behaviour of a lens depends on the relative refractive index of the lens material with respect to the surrounding medium.",
     AR_OPTIONS, 0, "Both true, R explains A", "Lens maker's formula contains (n_lens/n_medium - 1).", None),
    (9, "SA", 2, 2, "An object is placed 15 cm from a concave mirror of focal length 10 cm. Find the position and magnification of the image.",
     None, None, "v = -30 cm (30 cm in front of the mirror); m = -2",
     "1/v + 1/u = 1/f with u = -15, f = -10 gives v = -30 cm; m = -v/u = -2, so the image is real, inverted and twice as large.",
     "1 mark for the image position, 1 mark for magnification with its meaning."),

    # ---------------- Chapter 10
    (10, "MCQ", 1, 1, "In Young's double slit experiment, if the slit separation is halved, the fringe width",
     ["halves", "doubles", "remains the same", "becomes four times"], 1, "doubles", "beta = lambda D / d.", None),
    (10, "MCQ", 1, 1, "For a sustained interference pattern, the two sources must be",
     ["incoherent", "coherent", "of different frequencies", "of different amplitudes only"], 1, "coherent",
     "A stable phase relationship is required.", None),
    (10, "MCQ", 1, 2, "In single slit diffraction of slit width a, the width of the central maximum on a screen at distance D is",
     ["lambda D / a", "2 lambda D / a", "lambda D / 2a", "a D / lambda"], 1, "2 lambda D / a",
     "The first minima are at +/- lambda D/a.", None),
    (10, "MCQ", 1, 1, "According to Huygens' principle, every point on a wavefront acts as",
     ["an absorber", "a secondary source of wavelets", "a node", "a polariser"], 1, "a secondary source of wavelets",
     "This is the statement of the principle.", None),
    (10, "AR", 1, 2, "Assertion (A): With white light in Young's double slit experiment, the central fringe is white. Reason (R): At the centre the path difference is zero for every wavelength.",
     AR_OPTIONS, 0, "Both true, R explains A", "Zero path difference gives constructive interference for all wavelengths.", None),
    (10, "SA", 2, 2, "In Young's double slit experiment, the slits are 0.50 mm apart and the screen is 1.0 m away. Light of wavelength 600 nm is used. Calculate the fringe width.",
     None, None, "1.2 mm", "beta = lambda D/d = 600e-9 x 1.0 / 0.50e-3 = 1.2e-3 m.",
     "1 mark for the formula and substitution, 1 mark for the value with unit."),

    # ---------------- Chapter 11
    (11, "MCQ", 1, 1, "The maximum kinetic energy of photoelectrons depends on",
     ["the intensity of light only", "the frequency of light only", "both intensity and frequency", "the area of the metal"], 1, "the frequency of light only",
     "Kmax = h nu - phi.", None),
    (11, "MCQ", 1, 2, "The de Broglie wavelength of an electron accelerated through a potential difference V is approximately",
     ["12.27 / sqrt(V) angstrom", "12.27 x sqrt(V) angstrom", "1.227 / V angstrom", "0.1227 V angstrom"], 0, "12.27 / sqrt(V) angstrom",
     "Standard result for electrons.", None),
    (11, "MCQ", 1, 1, "The stopping potential in a photoelectric experiment depends on",
     ["the intensity of incident light", "the frequency of incident light", "the area of the emitter", "the distance of the source"], 1, "the frequency of incident light",
     "eV0 = h nu - phi.", None),
    (11, "MCQ", 1, 2, "The energy of a photon of wavelength 500 nm is approximately",
     ["1.24 eV", "2.48 eV", "3.10 eV", "4.96 eV"], 1, "2.48 eV", "E = 1240/500 eV = 2.48 eV.", None),
    (11, "AR", 1, 2, "Assertion (A): The photoelectric effect shows the particle nature of light. Reason (R): Emission is instantaneous and the maximum kinetic energy depends on frequency, not intensity.",
     AR_OPTIONS, 0, "Both true, R explains A", "These observations contradict the classical wave picture.", None),
    (11, "SA", 2, 2, "A metal has work function 2.0 eV. Light of photon energy 3.0 eV is incident on it. Calculate the maximum kinetic energy and the stopping potential.",
     None, None, "1.0 eV; stopping potential 1.0 V",
     "Kmax = 3.0 - 2.0 = 1.0 eV; stopping potential equals Kmax in electron volts, so 1.0 V.",
     "1 mark for Kmax, 1 mark for the stopping potential with unit."),

    # ---------------- Chapter 12
    (12, "MCQ", 1, 1, "The radius of the nth Bohr orbit of hydrogen varies as",
     ["n", "n^2", "1/n", "1/n^2"], 1, "n^2", "r = 0.53 n^2 angstrom.", None),
    (12, "MCQ", 1, 1, "The energy of the electron in the n = 2 state of hydrogen is",
     ["-13.6 eV", "-6.8 eV", "-3.4 eV", "-1.51 eV"], 2, "-3.4 eV", "En = -13.6/n^2.", None),
    (12, "MCQ", 1, 1, "Rutherford's alpha particle scattering experiment established that",
     ["the atom is neutral", "the nucleus is small and positively charged", "electrons revolve in fixed orbits", "energy is quantised"], 1, "the nucleus is small and positively charged",
     "Large-angle scattering from a small massive positive centre explains the data.", None),
    (12, "MCQ", 1, 2, "The Lyman series of the hydrogen spectrum lies in the",
     ["visible region", "ultraviolet region", "infrared region", "microwave region"], 1, "ultraviolet region",
     "Transitions to n = 1 have photon energies in the ultraviolet.", None),
    (12, "AR", 1, 2, "Assertion (A): The radius of the nth Bohr orbit increases as n^2. Reason (R): The angular momentum of the electron is quantised in units of h/2pi.",
     AR_OPTIONS, 0, "Both true, R explains A", "Quantisation of angular momentum together with the Coulomb force law gives r proportional to n^2.", None),
    (12, "SA", 2, 2, "Calculate the energy required to excite a hydrogen atom from the ground state to the n = 2 state.",
     None, None, "10.2 eV", "E = -3.4 - (-13.6) = 10.2 eV.",
     "1 mark for the levels used, 1 mark for the value with unit."),

    # ---------------- Chapter 13
    (13, "MCQ", 1, 1, "The binding energy per nucleon is maximum near the mass number",
     ["4", "56", "120", "238"], 1, "56", "The curve peaks near iron (A about 56).", None),
    (13, "MCQ", 1, 2, "The density of a nucleus is",
     ["proportional to A", "proportional to A^(1/3)", "independent of A", "proportional to 1/A"], 2, "independent of A",
     "R = R0 A^(1/3) and mass is proportional to A, so density is constant.", None),
    (13, "MCQ", 1, 1, "Energy is released in nuclear fission because",
     ["the total mass increases", "the total mass decreases", "the charge decreases", "the nucleus splits into equal parts"], 1, "the total mass decreases",
     "Mass defect appears as energy.", None),
    (13, "MCQ", 1, 1, "The energy equivalent of one atomic mass unit is",
     ["931.5 MeV", "931.5 keV", "1.6 MeV", "8 MeV"], 0, "931.5 MeV", "1 u = 931.5 MeV/c^2.", None),
    (13, "AR", 1, 2, "Assertion (A): Nuclear fusion releases energy for light nuclei. Reason (R): The binding energy per nucleon increases with mass number up to about A = 56.",
     AR_OPTIONS, 0, "Both true, R explains A", "Moving towards the peak of the curve releases energy.", None),
    (13, "SA", 2, 2, "A nucleus has a mass defect of 0.030 u. Calculate the energy released.",
     None, None, "27.9 MeV", "E = 0.030 x 931.5 = 27.9 MeV.",
     "1 mark for the conversion factor, 1 mark for the value with unit."),

    # ---------------- Chapter 14
    (14, "MCQ", 1, 1, "In an intrinsic semiconductor at a given temperature",
     ["only electrons conduct", "only holes conduct", "the number of electrons equals the number of holes", "there are no charge carriers"], 2, "the number of electrons equals the number of holes",
     "Thermal generation creates electron-hole pairs.", None),
    (14, "MCQ", 1, 1, "Doping silicon with a pentavalent impurity produces",
     ["a p-type semiconductor", "an n-type semiconductor", "an insulator", "an intrinsic semiconductor"], 1, "an n-type semiconductor",
     "The fifth valence electron is loosely bound and becomes a free carrier.", None),
    (14, "MCQ", 1, 2, "A p-n junction diode in forward bias has",
     ["very high resistance", "low resistance", "infinite resistance", "zero capacitance"], 1, "low resistance",
     "The barrier potential is reduced, so the current is large.", None),
    (14, "MCQ", 1, 1, "The energy gap of silicon at room temperature is about",
     ["0.1 eV", "1.1 eV", "3.0 eV", "5.4 eV"], 1, "1.1 eV", "Silicon: about 1.1 eV; germanium: about 0.7 eV.", None),
    (14, "AR", 1, 2, "Assertion (A): A p-n junction diode conducts appreciably in forward bias. Reason (R): The applied forward voltage reduces the potential barrier at the junction.",
     AR_OPTIONS, 0, "Both true, R explains A", "A lower barrier allows majority carriers to cross.", None),
    (14, "SA", 2, 2, "A full-wave rectifier is supplied with an alternating input of frequency 50 Hz. What is the frequency of the output ripple? Justify briefly.",
     None, None, "100 Hz", "Both half cycles are rectified, so the ripple frequency is twice the input frequency.",
     "1 mark for the value, 1 mark for the justification."),
]


def main():
    items = []
    for i, (ch, fmt, marks, diff, q, opts, ans_idx, ans_text, sol, rubric) in enumerate(BANK, 1):
        items.append({
            "id": f"C{ch:02d}-Q{i:03d}",
            "chapter": ch,
            "chapter_name": CH[ch],
            "format": fmt,
            "marks": marks,
            "difficulty": diff,
            "question": q,
            "options": opts,
            "answer_index": ans_idx,
            "answer_text": ans_text,
            "solution": sol,
            "rubric": rubric,
            "source_class": "ORIGINAL",
            "source_reference": "Authored for this project in CBSE style; not a previous-year question",
            "verification_status": "author-verified (single author, self-checked against NCERT scope)",
            "syllabus_version": "2026-27",
            "assessment_version": "1.0",
            "copyright": "Original content, free to use within this project",
        })
    bank = {
        "bank_version": "1.0.0",
        "syllabus_version": "2026-27",
        "created": "2026-11-15",
        "item_count": len(items),
        "chapters_covered": sorted({i["chapter"] for i in items}),
        "formats": ["MCQ", "AR", "SA"],
        "provenance_statement": (
            "All items are original. No CBSE previous-year question text and no MTG content is "
            "reproduced. The bank exists to operate the diagnostic engine."),
        "licence_note": "Original educational content authored for this project.",
        "items": items,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(bank, indent=1), encoding="utf-8")
    per = {c: sum(1 for i in items if i["chapter"] == c) for c in CH}
    print("wrote", OUT.relative_to(ROOT), "items:", len(items))
    print("per chapter:", per)
    # integrity: every MCQ/AR has 4 options and a valid answer index
    for it in items:
        if it["options"]:
            assert len(it["options"]) == 4, it["id"]
            assert it["answer_index"] in (0, 1, 2, 3), it["id"]
        else:
            assert it["format"] == "SA" and it["answer_text"], it["id"]
    print("integrity checks passed")


if __name__ == "__main__":
    main()
