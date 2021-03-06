"""
This is a PyMOL script for analyzing shifts in preferences on the structure 5FYL

It colors the structure of Env according to site-specific RMSD_corrected values
on a color scale from white (no shift) to red (large shift), with sites with
significant RMSD_corrected values shown as spheres.

When `take_pictures` is set to true, this script generates pictures of Env:
`5FYL_pymol_face1.png` and `5FYL_pymol_face2.png`, which are rotated 120 degrees
relative to one another.

This script intended to be run in the PyMOL terminal as:
	run pymol_analysis_5FYL.py

Hugh Haddox, November-27-2017
"""

# Imports
import pymol
from pymol import cmd

# Fetch structure
structure = '5FYL'
cmd.reinitialize()
cmd.delete('all')
cmd.fetch(structure) #, type='pdb1')

# Remove non-Env chains
# gp41 = chain B
# gp120 = chain G
# 35O22 = chains D and E
# PGT122 = chains H and L
cmd.remove ('c;D,E,H,L,U,V')

# Generate symmetry partners based on crystal structure
cmd.symexp(structure, structure, structure, 3)

# Tweak initial display and color of Env monomers
cmd.hide('everything')
cmd.bg_color('white')
cmd.show('cartoon')
cmd.color('grey40')
#cmd.color('grey20', structure)
cmd.set('cartoon_transparency', '0.5')
cmd.set('cartoon_transparency', '0', structure)
#cmd.hide('hetatm')

# Identify unique sites in structure
sites_in_structure = []
cmd.iterate("(name ca)","sites_in_structure.append(resi)")
unique_sites_in_structure = []
for site in sites_in_structure:
	if site not in unique_sites_in_structure:
		unique_sites_in_structure.append(site)

# Get site-specific RMSDcorrected values and whether the shift at a site is
# significant
RMSD_dict = {}
sig_dict = {}
with open('../BG505_to_BF520_prefs_dist.csv') as f:
	lines = f.readlines()[1:]
	for line in lines:
		elements = line.split(',')
		site = elements[0]
		RMSDcorrected = elements[1]
		significant_shift = elements[6]
		RMSD_dict[site] = float(RMSDcorrected)
		sig_dict[site] = significant_shift
sig_sites = [site for site in sig_dict if sig_dict[site]=='True']
min_RMSD = min(RMSD_dict.values())
max_RMSD = max(RMSD_dict.values())
print "\nThe minimum and maximum RMSDcorrected values are:"
print "min: {0}".format(min_RMSD)
print "max: {0}".format(max_RMSD)

# Color residues by omega-by-site log10P values
sites_with_data = RMSD_dict.keys()
sites_not_in_structure = []
for site in sites_with_data:
	#print(site, RMSD_dict[site])
	cmd.alter("{0} and resi {1}".format(structure, site),
				"b = {0}".format(RMSD_dict[site]))
	if site not in unique_sites_in_structure:
		sites_not_in_structure.append(site)
color_scheme = 'white_red'
cmd.spectrum('b', color_scheme, structure, minimum=min_RMSD, maximum=max_RMSD)
print ("\nSites with data not in structure: {0}".format(
								', '.join(sites_not_in_structure)))
print ("Sites with significant shifts not in structure: {0}".format(
								', '.join(s for s in sig_sites
											if s in sites_not_in_structure)))

# Color residues lacking data black
sites_lacking_data = [site for site in unique_sites_in_structure if site not in sites_with_data]
print ("\nThe following sites in the structure, but lacking data will be colored white: {0}".format(', '.join(sites_lacking_data)))
cmd.color('black', '{0} and resi {1}'.format(structure, '+'.join(sites_lacking_data)))

# Show significant sites as spheres
print ("\nThere are {0} sites with significant RMSD corrected values".format(len(sig_sites)))
print (', '.join(sig_sites))
cmd.select('sig_RMSDcorrected', '{0} and resi {1}'.format(structure, '+'.join(sig_sites)))
cmd.show('spheres', 'sig_RMSDcorrected')

# Report how many significant sites are in the structure
sig_site_in_structure = [site for site in sig_sites if site in unique_sites_in_structure]
print ("\nOf the significant sites, {0} of them are in the structure".format(len(sig_site_in_structure)))

# Take a pictures of Env rotated 120 degrees relative to one another
cmd.set_view ("""\
	 0.606518745,   -0.016123615,    0.794892550,\
	 0.760999739,    0.301236391,   -0.574545264,\
	-0.230190367,    0.953389049,    0.194983304,\
	 0.000000000,    0.000000000, -364.900909424,\
   165.407760620,  160.255493164,  155.138549805,\
   225.052154541,  504.749664307,  -20.000000000 """)

take_pictures = False
if take_pictures:
	cmd.bg_color('white')
	cmd.png('{0}_pymol_face1.png'.format(structure), width=1000, dpi=1000, ray=1)
	cmd.rotate('y', '120')
	cmd.png('{0}_pymol_face2.png'.format(structure), width=1000, dpi=1000, ray=1)

# Identify sites that have substituted
substituted_sites = []
with open('../BG505_to_BF520_prefs_dist.csv') as f:
	lines = f.readlines()[1:]
	for line in lines:
		(site, RMSDcorrected, RMSDbetween,RMSDwithin, BG505, BF520, significant_shift, substituted) = line.split(',')[:8]
		if substituted == 'True':
			substituted_sites.append(site)
substituted_sites = list(set(substituted_sites)) # for some reason, this is needed to handle duplicates
cmd.select('subs', structure + ' and resi ' + '+'.join(substituted_sites))
print("\nThere are {0} substituted sites:".format(len(substituted_sites)))
print(', '.join(substituted_sites))
subs_in_structure = [site for site in substituted_sites if site in unique_sites_in_structure]
print ("\nOf the substituted sites, {0} of them are in the structure".format(len(subs_in_structure)))

# Annotations of structural features
# gp120 and gp41
cmd.select('gp120', structure + ' and resi 31-511')
cmd.select('gp41', structure +' and resi 512-664')

# Variable loops
cmd.select('c1', structure +' and resi 31-131')
cmd.select('v1', structure +' and resi 132-156')
cmd.select('v2', structure +' and resi 158-195')
cmd.select('c2', structure +' and resi 196-295')
cmd.select('v3', structure +' and resi 296-330')
cmd.select('c3', structure +' and resi 331-385')
cmd.select('v4', structure +' and resi 386-417')
cmd.select('c4', structure +' and resi 418-459')
cmd.select('v5', structure +' and resi 460-470')
cmd.select('c5', structure +' and resi 471-511')
cmd.select('vloops', 'v1 v2 v3 v4 v5')

# Disulfides
cmd.select('disulfides', structure +' and resi 54+74+119+126+131+157+196+205+218+228+239+247+296+331+378+385+418+445')

# CD4 binding site
cmd.select('cd4bs', structure +' and resi 124-127+196+198+279-283+365-370+374+425-432+455-461+469+471-477') # Zhou et al. 2010 PMID 20616231; Supplemental Fig. S1

# co-receptor binding site
cmd.select('cxcr4_bs_mutagenesis', structure +' and resi 298+308+315+317+421+422') # Basmaciogullari et al., 2002
cmd.select('ccr5_bs_mutagenesis', structure +' and resi 121+123+207+381+420+421+422+438+440+441') # Rizzuto et al., 1998
cmd.select('coreceptor_bs_GPGR', structure +' and resi 312-315')

# Antibody epitopes determined in previous computational analyses
cmd.select('CD4bs_epitope', structure + ' and resi 96+97+98+102+122+124+198+275+276+278+279+280+281+282+283+354+357+365+366+367+368+370+371+425+426+427+428+429+430+431+432+455+456+457+458+459+460+461+462+463+465+466+467+469+472+473+474+476+480')
cmd.select('V3_epitope', structure + ' and resi 135+136+137+156+301+322+323+324+325+326+327+328+330+332+373+384+386+389+392+409+415+417+418+419+442+444')
cmd.select('V1_V2_epitope', structure + ' and resi 156+158+160+162+163+164+165+166+167+168+169+170+171+172+173')
cmd.select('gp120_gp41_epitope', structure + ' and resi 44+45+46+58+80+82+83+84+85+87+88+90+91+92+93+94+229+230+231+232+234+237+238+240+241+245+246+262+276+277+278+352+448+462+512+513+514+515+516+517+518+519+520+521+522+527+529+542+543+549+550+554+592+611+613+615+616+617+618+620+621+624+625+627+629+630+632+633+634+636+637+638+640+641+643+644+647')
cmd.select('fusion_peptide', structure + ' and resi 512-527')
cmd.select(None)
