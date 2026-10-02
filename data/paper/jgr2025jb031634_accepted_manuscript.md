# Source: accepted manuscript, https://escholarship.org/uc/item/5fc7v9k7 (PDF https://escholarship.org/content/qt5fc7v9k7/qt5fc7v9k7.pdf), CC BY 4.0. Text extraction of the PDF; figures not included.

## **Lawrence Berkeley National Laboratory**

### **LBL Publications**

### **Title**

Insights Into Seismicity Associated With Flexibly Operating Enhanced Geothermal System

From Real‐Time Distributed Acoustic Sensing

### **Permalink**

https://escholarship.org/uc/item/5fc7v9k7

### **Journal**

Journal of Geophysical Research: Solid Earth, 130(7)

### **ISSN**

2169-9313

### **Authors**

Chamarczuk, Michal

Ajo‐Franklin, Jonathan

Nayak, Avinash

et al.

### **Publication Date**

2025-07-01

### **DOI**

10\.1029/2025jb031634

### **Copyright Information**

This work is made available under the terms of a Creative Commons Attribution License,

available at https://creativecommons.org/licenses/by/4.0/

Peer reviewed

eScholarship.org Powered by the California Digital Library

University of California

manuscript submitted to _JGR: Solid Earth_

### **Insights Into Seismicity associated with Flexibly Operating Enhanced Geothermal**

1

### **System from Real-time Distributed Acoustic Sensing**

2

**Michal Chamarczuk** **1** **, Jonathan Ajo-Franklin** **1** **, Avinash Nayak** **3** **, Jack Norbeck** **2** **, Tim** 3 **Latimer** **2** **, Aleksei Titov** **2** **, Sireesh Dadi** **2** 4

1Department of Earth, Environmental, and Planetary Sciences, Rice University, Houston, TX, 5

### USA

6

2Fervo Energy, Houston, TX, USA 7

3Lawrence Berkeley National Laboratory, CA, USA 8

9

### Corresponding author: Michal Chamarczuk, Jonathan Ajo-Franklin (chamarczukm@gmail.com,

10

### ja62@rice.edu)

11

12

### **Key Points:**

13

### • Real-time distributed acoustic sensing (DAS) reveals pressure-dependent behavior of

14

### seismicity during cyclic EGS operations

15

16

### • The spatio-temporal evolution of microseismic clouds recorded during cyclic injection

17

### cycles exhibit diffusive-like properties

18

19

### • Combining DAS with edge computing shows the potential to inform protocols for

20

### induced seismicity mitigation in an EGS context

21

22

manuscript submitted to _JGR: Solid Earth_

### **Abstract**

23

### Enhanced Geothermal Systems (EGS) have the capacity to broaden the accessible resource pool

24

### for geothermal power generation. Traditionally viewed as a 'baseload' resource, their flexible

25

### operation might also enable dispatchable load-following generation and long-term energy

26

### storage, aligning them with the evolving landscape of decarbonized electricity systems.

27

### However, increasing permeability and extracting energy during EGS operations can induce

28

### microseismic events; for many prior EGS efforts, some associated seismicity has been observed.

29

### While energetically beneficial, the flexibility of EGS operations prompts our inquiry into

30

### whether new types of operations will yield previously unseen seismicity patterns.

31

### We demonstrate the use of distributed acoustic sensing (DAS) with real-time edge computing to

32

### monitor seismicity during a pilot test of a cyclically operated EGS facility at the Blue Mountain

33

### geothermal field. Our focus lies in uncovering seismicity insights from the real-time

34

### microseismic catalog, particularly during load-following dispatchability tests simulating flexible

35

### EGS operation. We find that variations in pore pressure consistently correlate with seismicity,

36

### and that controlling pressure cycles during flexible operations appears to constrain microseismic

37

### activity during subsequent cycles. The spatio-temporal evolution of microseismic clouds

38

### recorded during cyclic injection cycles fits diffusive models over our available observation

39

### period. Additionally, seismicity elevation lags behind pore pressure increases, likely due to

40

### pressure diffusion to the fracture system boundary. Through real-time monitoring, we offer novel

41

### insights into seismicity associated with flexibly operating EGS. Our findings suggest that

42

### leveraging DAS and edge computing can inform EGS operations and help mitigate induced

43

### seismicity.

44

### **Plain Language Summary**

45

### Enhanced Geothermal Systems (EGS) enhance subsurface permeability to allow fluid circulation

46

### through hot rock formations deep underground. EGS development uses high-pressure fluid

47

### injections to create or reopen fractures. While geothermal power is often viewed as a steady-state

48

### (baseload) resource, increasing demand for flexible, low-carbon power generation highlights the

49

### potential of EGS to adapt to fluctuating energy needs and store energy longer, aiding transition to

50

### cleaner electricity systems.

51

### It is known that conventional EGS operations can trigger microseismic events, but seismicity

52

### related to flexible operations, like cyclic injections, is less studied. To investigate this, we

53

### developed a real-time seismic acquisition and processing framework that uses borehole

54

### distributed acoustic sensing (DAS) to monitor small seismic events during flexible EGS

55

### operations. This system operates on the “edge,” meaning computation happens close to where

56

### data is collected, avoiding the need to transfer large datasets for analysis. We deployed this

57

### framework during an EGS pilot at Blue Mountain, where flexible production methods were

58

### tested. Our results showed a consistent relationship between changes in pore pressure and

59

### seismic activity. Seismicity during injection cycles exhibited a diffusive pattern, and there was a

60

manuscript submitted to _JGR: Solid Earth_

### delay in seismic activity following pressure changes, offering insights that could improve

61

### seismicity mitigation strategies.

62

63

### **1 Introduction**

64

65

### Geothermal energy production is considered one of the key reliable and sustainable low-carbon

66

### electricity technologies that can provide energy in all seasons and over long durations (e.g., weeks

67

### or longer; Sepulveda et al., 2018), where available. While geothermal energy currently comprises

68

### only 0.4% of total electricity generation capacity in the United States (EIA, 2021), the development

69

### of enhanced geothermal systems (EGS) may be an important technological breakthrough that will

70

### allow geothermal development to extend beyond scarce, naturally formed hydrothermal reservoirs,

71

### thus enabling widespread deployment and geothermal energy production in the future (Augustine

72

### et al., 2019, 2023). Hydrothermal systems, occurring naturally, rely on three crucial components—

73

### heat, fluid, and formation permeability—for electricity generation. However, in some locations,

74

### although underground rock retains heat, natural permeability or fluid presence may be insufficient.

75

### In such cases, EGS can be deployed to create engineered reservoirs, enabling the harnessing of

76

### heat energy for electricity generation at economically competitive costs (e.g., Majer et al., 2005,

77

### Horne et al. 2025). EGS reservoirs are often hosted by deep crystalline rock overlain by a 3–5

78

### kilometers of insulating sediment which mitigates heat loss (e.g., Majer et al., 2005). The primary

79

### method for extracting heat energy from deep rocks involves circulating water or another working

80

### fluid through them to extract heat. These rocks often lack porosity, and flow must occur through

81

### the enhancement of natural fractures or the creation of new hydraulic pathways, a process referred

82

### to as stimulation (e.g., Majer et al., 2007; Dyer et al., 2008).

83

84

### During EGS stimulation and subsequent production, microseismic events and, critically, a small

85

### number of felt earthquakes, can be generated (Majer et al., 2005, Baria et al. 2005, Gonzalez,

86

### 2022). Previous studies have established a correlation between various activities associated with

87

### geothermal energy extraction, such as fluid extraction, cooling, and reinjection, with the

88

### occurrence of microseismic events as part of the fracturing process (Asanuma et al., 2007; Buijze

89

### et al., 2019). The microseismic and hydraulic data recorded during stimulation enables evaluation

90

### of zones where fractures have been created or reactivated, often referred to as the stimulated

91

### reservoir volume (SRV); in some cases, the resulting information can be used to guide the

92

### trajectories of subsequent production wells and completion activities. We should note that the

93

### microseismic SRV is not necessarily the zone of flowing connected fractures relevant to heat

94

### transfer but rather the domain where some form of seismic failure has occurred. Microseismic

95

### monitoring can also be used to assist in evaluating the risk of induced seismic events of concern

96

### to infrastructure and the broader community. Regulators commonly deploy traffic light schemes

97

### (TLSs) that contain guidelines to adjust injection activities by reducing, pausing, or halting

98

### operations if the magnitude of the largest seismic event exceeds a predetermined threshold (e.g.,

99

### Bosman et al., 2016; Baisch et al., 2019; Clarke et al., 2019). The thresholds are generally set

100

### below the actual magnitude the operators wish to avoid (e.g., Clarke et al., 2019). The perceived

101

### risk of induced seismicity in areas utilizing EGS is a significant barrier to EGS acceptance (Ricks

102

### et al., 2024); damaging seismic events have resulted in the suspension of several EGS projects

103

manuscript submitted to _JGR: Solid Earth_

### (Deichmann et al., 2009; Ellsworth et al., 2019; Grigoli et al., 2018). Addressing societal concerns

104

### is paramount for advancing integration of EGS into future electricity infrastructure. This

105

### combination of information on stimulation efficiency and seismic hazard make real-time

106

### microseismic monitoring one of the key diagnostic tools in the context of EGS (Clarke et al., 2019,

107

### Kwiatek et al., 2019).

108

109

### Prior studies, both for reservoir management and power utilization, largely envision EGS

110

### facilities as baseload resources, operating at their maximum rated output over large time scales

111

### (e.g., Baik et al., 2021). However, due to the ongoing decarbonization of the grid through the large-

112

### scale deployment of variable renewable energy resources such as wind and solar, the role of EGS

113

### systems may shift to utilization as a dispatchable power source, with a diverse portfolio of

114

### complementary clean energy technologies expected to minimize the overall costs. Using a novel

115

### modelling framework, Ricks et al. (2022) demonstrated that EGS can provide high-capacity energy

116

### storage by alternately accumulating and discharging pressurized working fluids within engineered

117

### fracture network. The in-reservoir geomechanical energy storage allows EGS plants to decrease

118

### energy production when there is an excess of electricity on the grid and increase it during times of

119

### shortage, thus providing means to adjust the energy production schedule. While seismicity

120

### associated with EGS is relatively well-documented, including major EGS activities like

121

### hydrofracturing and fluid injection (Baria et al., 2005; Majer et al., 2007), there remains limited

122

### empirical studies of the seismicity implications for flexible EGS operations, particularly, repeated

123

### short (~ 12 hours) charge–discharge cycles (Ricks et al., 2022). Whereas seismicity rates are

124

### generally correlated with injection or production activities over short or long time scales (Johnson

125

### et al., 2016), a few studies have reported the presence of post-injection seismicity, where

126

### magnitude of event may still increase after the operations have ceased (e.g., Häring et al., 2008;

127

### Davatzes et al., 2013; Clarke et al., 2014; Cardiff et al., 2018; Clarke et al., 2019; Gonzales et al.,

128

### 2022). Additionally, EGS practices are quickly evolving from hydroshearing approaches to

129

### systems with completion strategies more similar to unconventional shale development including

130

### multi-stage propped hydraulic fracturing (Norbeck & Latimer, 2023), which motivates the

131

### investigation of any changes in the resulting induced seismicity.

132

### Flexible EGS operations were recently evaluated at the Blue Mountain geothermal area as

133

### part of a commercial pilot managed by Fervo Energy (Norbeck & Latimer, 2023). The Blue

134

### Mountain experiment aimed to drill, complete, and operate horizontal EGS wells within a high-

135

### temperature, hard rock environment and utilize unconventional completion strategies including

136

### multiple stages and large proppant loads. Results from this experiment showcased the feasibility

137

### of flexible EGS systems in real-world settings; the pilot injector/producer pair yielded and

138

### economically viable flowrate equivalent to peak gross electric power output of 3.5 MW. This study

139

### presents findings from a real-time microseismic monitoring system deployed to track the Blue

140

### Mountain EGS experiment, with a particular focus on the crossflow test between horizontal wells

141

### and a series of load-following dispatchability tests (Norbeck & Latimer, 2023).

142

### Our study focuses on the impact of cyclically varying injections on seismicity and the

143

### resulting implications for controlling injection strategies. To achieve this, we analyze the

144

### microseismicity, its magnitude-frequency distribution, and the resulting spatiotemporal

145

### characteristics throughout the entire experiment. We leverage a downhole DAS dataset acquired

146

### on a fiber-optic cable in a vertical monitoring well using a dedicated real-time workflow to provide

147

### real-time microseismic feedback. We begin with a concise overview of the core aspects of our

148

manuscript submitted to _JGR: Solid Earth_

### study mainly seismic activity linked to Enhanced Geothermal Systems (EGS) and the role of

149

### Distributed Acoustic Sensing (DAS) in real-time monitoring of such systems. We then introduce

150

### the Blue Mountain EGS experiment. We briefly describe the monitoring system architecture and

151

### processing workflow that enabled effective and efficient real-time microseismic monitoring of the

152

### flexible EGS operations using downhole DAS data despite the challanges of large data volumes

153

### (~10 GB/hour). We produced a microseismic catalog spanning two months, revealing pressure-

154

### dependent seismicity behavior throughout the experiment's duration. We then conduct a focused

155

### examination of the flexible operations phase of the Blue Mountain experiment, characterizing the

156

### spatiotemporal dynamics of seismic activity during cyclic injection cycles. Using the concept of a

157

### triggering front and a linear diffusion approximation, we delineate the diffusive spatiotemporal

158

### evolution of microseismicity as a cloud of events, wherein propagation is controlled by an effective

159

### diffusivity of approximately 0.43 m²/s. We base our analysis on event distances relative to the

160

### horizontally oriented injection well, using the vertical distribution of seismic events. Our key

161

### findings include an observed time-delay in seismicity elevation with respect to pressure increase

162

### and a rapid decrease in seismicity levels coinciding with production level reductions within

163

### individual injection cycles. We observe significant pressure-dependent seismicity behavior, with

164

### the number of spikes correlating temporally and numerically with charging and discharging cycles,

165

### and seismicity leveling off between subsequent cycles.

166

167

### **2 DAS for real-time microseismic monitoring in EGS**

168

169

### The mitigation of induced seismicity is generally based on monitoring of two microseismic-based

170

### phenomena: (1) consistency of largest observed magnitudes at fluid injection sites with the

171

### sampling statistics of the Gutenberg-Richter distribution for tectonic earthquakes (van der Elst et

172

### al., 2016), and (2) the alignment of microseismic events along the fault structure. In the event of

173

### fault reactivation being detected during injection, or if projected magnitudes based on planned

174

### injection volumes surpass the designated threshold, the stimulation process can be redirected away

175

### from areas displaying fault reactivation, and/or the injection volumes (or pressures) could be

176

### decreased (Kwiatek et al., 2019; Clarke et al. 2019). Successfully achieving these two goals in

177

### addition to accurately characterizing the stimulated reservoir volume (e.g., Verdon et al., 2019)

178

### requires observational and processing tools for generating high quality microseismic catalogs that

179

### capture the numerous low magnitude events to delineate spatial zones of failure. State-of-the-art

180

### downhole geophone arrays, typically comprised of 10-50 geophones deployed in one or more wells

181

### (e.g., Maxwell et al., 2010), when coupled to modern processing tools, allow for real-time

182

### acquisition of microseismic catalogs consisting of up to hundreds of thousands of events with

183

### precise locations, covering several orders of magnitude (e.g., Zinno et al., 1998). However, in the

184

### context of EGS, downhole monitoring entails close proximity to the reservoir and necessitates

185

### long-term acquisition under hostile high temperature (>200°C) and high pressure conditions,

186

### factors that can pose challenges for the use of geophones, particularly when downhole digitization

187

### is required (Cai et al., 2019).

188

189

### The above-mentioned challenges have motivated researchers to explore all-optical

190

### microseismic monitoring approaches, particularly DAS-based systems, which have demonstrated

191

manuscript submitted to _JGR: Solid Earth_

### sustained performance in demanding environments (e.g., Lellouch et al., 2021; Li et al., 2024a,

192

### 2024b). Since the glass in optical fibers can withstand high temperatures, the temperature limit of

193

### these systems is typically dictated by the polymer fiber coatings (e.g., <300 °C for polyimide). The

194

### key aspects of DAS that are relevant for pushing the limits of event detection and recording high

195

### coherency wavefronts are: (i) The large number of channels available (e.g., 1000-3000 channels

196

### in boreholes), (ii) the resulting dense spatial sampling (e.g., 1 m) and (iii) high sampling frequency

197

### (e.g., 10 kHz). For an overview of DAS technology, as well as a discussion of its advantages

198

### specific for EGS borehole monitoring, we refer the interested reader to a range of recent studies

199

### (Lellouch et al., 2020, 2021; Li et al., 2024a; Verdon et al., 2019, Karrenbach et al., 2019; Bahrach

200

### et al., 2023).

201

202

### Of particular relevance to this study, Lellouch et al. (2020) conducted a thorough

203

### comparison of monitoring performance in the context of EGS, (specifically at the Utah FORGE

204

### site), between downhole geophones and DAS. They reported that while DAS exhibited slightly

205

### inferior detection performance in direct one-to-one comparisons with single geophones, it proved

206

### capable of detecting seismic events originating from newly created fractures near the stimulation

207

### well and enabled reliable magnitude estimation. Additionally, a subsequent DAS monitoring study

208

### in the same area (Lellouch et al., 2021) demonstrated DAS's suitability for detecting more distant

209

### seismic activity unrelated to the stimulated fractures. An important conclusion drawn from

210

### Lellouch et al.'s (2020) study, pertinent to our research, is the capacity of borehole DAS monitoring

211

### for generating high-quality seismicity catalogs that facilitate the estimation of b-values, a crucial

212

### parameter for understanding induced seismicity (e.g., Maxwell et al., 2009a; Verdon & Budge,

213

### 2018; Kettlety et al., 2019). Coupled with performance at high temperatures and the possibility of

214

### deployment in active wells, DAS has emerged as a promising option for cost-effective, long-term

215

### monitoring of EGS projects.

216

217

manuscript submitted to _JGR: Solid Earth_

218

### **Figure 1** . The Blue Mountain EGS Pilot site (40.98°N, 118.12°W). (a) Aerial view of the Blue

219

### Mountain field in Nevada, USA. The observation well (73-22) is denoted with white circle. (b)

220

### Picture of the Fervo Energy enhanced geothermal demonstration site in northern Nevada. (c) Depth

221

### section of the well geometries including deviated EGS doublet (34-22, 34A-22) and the vertical

222

### observation well (73-22).

223

224

### One of the central challenges associated with using DAS in real-time monitoring applications is

225

### the need to process and store very large data volumes, typically in field environments with

226

### insufficient telemetry bandwidth to transfer raw data (e.g., Spica et al., 2023). The potential of

227

### transitioning DAS-based monitoring systems from post-hoc to real-time analysis for conventional

228

### geothermal systems was demonstrated in a recent study by Azzola et al. (2023). In their research,

229

### DAS was incorporated into the seismic monitoring of a geothermal field in Munich, Germany

230

### (Azzola et al., 2023), where they introduced a proof-of-concept processing approach. In this study,

231

### we successfully developed and deployed an onsite or edge computing framework that performs

232

### event detection, location, and magnitude estimation and uploads the result to the cloud within a

233

### time frame shorter than the interval between acquiring two consecutive recordings.

234

235

### **3 Data and Monitoring Architecture**

236

### 3\.1 Blue Mountain EGS experiment

237

### The Blue Mountain EGS project site, managed by Fervo Energy, is situated in close proximity to

238

### an operational geothermal power station in northern Nevada (Figure 1a). This initiative targeted

239

### the hot (~180°C to ~200°C) low permeability areas at the margins of an active hydrothermal

240

### system to demonstrate the viability of horizontal drilling and multistage stimulation in geothermal

241

### formations under high temperature conditions (Fercho et al., 2023). EGS development at the site

242

### involved the drilling of three wells: a vertical monitoring well (73-22), a horizontal injector well

243

manuscript submitted to _JGR: Solid Earth_

### (34A-22), and a horizontal producer well (34A-22) (see Figure 1). The geological setting consists

244

### of slightly dipping alluvial sediments overlaying phyllite basement rocks intruded by igneous dikes

245

### and sills (Fercho et al., 2023; Norbeck & Latimer, 2023). Details regarding the geology of the Blue

246

### Mountain geothermal site are described in Fercho et al. (2023), while the EGS experiment was

247

### introduced by Norbeck and Latimer (2023) with subsequent analysis by Titov et al. (2024) and

248

### Dadi et al. (2024).

249

### The vertical monitoring well (73-22) was equipped with a permanent fiber optic monitoring cable

250

### behind casing, providing real-time DAS data for microseismic monitoring. This study analyzes

251

### three key parts of the experiment, the stimulation of the 34-22 production well, a crossflow

252

### production test lasting approximately 37 days to establish flow between the producer and injector

253

### wells, and a series of dispatchable load cycles, during which injection and/or production were

254

### increased. Throughout the experiment, a bottom hole pressure gauge installed outside the well

255

### casing at well 73-22 directly measured reservoir pressure. We use the pressure data to corroborate

256

### the observed spatio-temporal trends in microseismicity at the site. The drilling and stimulation

257

### phase took place between January 2022 and March 2023, with well testing occurring from April

258

### 2023 to May 2023. The real-time monitoring system developed in this study operated between

259

### March 15 and May 23, enabling the tracking of microseismicity related to stimulation, crossflow

260

### tests, and dispatchable loading cycles simulating flexible EGS system operation.

261

### In this study we put special emphasis on the flexible production cycles and investigate their imprint

262

### on the microseismicity recorded by our real-time system. Dispatchable loading cycles were

263

### designed to test EGS system operated in mode suitable for intermittent power needs and involved

264

### 5 cycles in total, three with restricted production followed by two where production was entirely

265

### halted during injection and allowed to flow unrestricted after 12 hours. This study focuses on two

266

manuscript submitted to _JGR: Solid Earth_

### questions, (1) what is the qualitative impact of varying pressure rates on seismicity? and (2) does

267

### microseismic activity reach initial equilibrium between subsequent cycles?

268

269

270

### **Figure 2** . Hardware/software architecture designed to monitor EGS pilot operations at Blue

271

### Mountain. (a) Real-time processing workflow consisting of four layers: edge, access, cloud, and

272

### storage. Fs, ds, and dx denote frequency sampling, data size, and spatial sampling, respectively.

273

### (b) Picture of the setup in the control room located on-site showing the hardware components:

274

### DAS interrogator, multicore processing server, RAID data storage units, and uninterruptible power

275

### supply (UPS).

276

### 3\.2 Monitoring architecture

277

278

### In this section, we describe our edge-based real-time microseismic monitoring system. DAS data

279

### is continuously acquired from the vertical monitoring well (73-22) at 1000 Hz at a 2 m spatial

280

### sampling, generating ~166 MB per minute, totaling 0.25 TB/day (with higher sampling rates

281

### reaching around 4 GB per minute). However, due to limitations in telemetry bandwidth,

282

### transferring and processing raw data off-site in real-time is typically not feasible, necessitating

283

### onsite processing at the data source, a configuration referred to as edge processing. Figure 2 shows

284

### the hardware architecture of edge data acquisition and processing system. The main components

285

### are the fiber optic cable cemented behind the production casing, the DAS interrogator unit (iDAS

286

### v.2, Silixa LLC), PC (equipped with a 12-core processor [i7-12700] and a consumer GPU [Nvidia

287

### GTX 1660]) serving as the edge processing station, RAID system (QNAP TS-1273U-8G), and

288

### satellite telemetry setup based on a Starlink system (Figure 2). The monitoring architecture is

289

manuscript submitted to _JGR: Solid Earth_

### divided into 4 components: the edge processing layer, and 3 parallel interaction layers: access,

290

### storage, and cloud. The data processing sequence proceeds as follows; (i) each minute, the DAS

291

### interrogator unit, connected with a high-performance local switch, writes raw DAS data to the

292

### RAID; raw data are processed onsite in real-time (edge layer) in repeatable cycles (<60 seconds),

293

### the resampled components, and products of processing are simultaneously transferred to the cloud

294

### (cloud layer) and RAID system (storage layer). The RAID system also serves as a local storage

295

### layer, allowing archiving of up to 4 months of continuous raw data. Key products such as automatic

296

### first-break picks, location reports, and graphical summaries in JPG format are exported to the cloud

297

### for further analysis and storage. Assuming, no power failures, or breaks in the satellite connection,

298

### at any point in time, the edge station and the control over processing workflow is accessible from

299

### the remote PC (access layer).

300

### The microseismic analysis process is performed on the edge processing workstation. The complete

301

### processing sequence used in this study is described in Text S1, with additional details on the event

302

### detection step provided in Text S2. We summarize the main components below. The total

303

### processing time (wall) is ~ 30 seconds for each 60 second record. For each step the approximate

304

### processing time breakdown is as follows:

305

### • File IO/polling (1.9 s)

306

### • Preprocessing (decimation, filtering, denoising) (4.1 s)

307

### • Event Detection (0.05 s)

308

### • Hypocenter Location (18-20 s)

309

### • Local ML estimation (1 s)

310

### • QC and LF products (2 s)

311

### • Cloud export (w. hourly reports) (2 s),

312

### where IO stands for Input/Output, ML is local magnitude, QC represents quality control, and LF

313

### denotes Low Frequency analysis.

314

### 3\.2.1 Location

315

### The key requirement for edge-based real-time location algorithms is sufficient computational

316

### efficiency to keep up with acquisition rates. In our system, raw data is transferred from the

317

### interrogator in 1 minute files leaving ~1 min to perform the entire processing sequence. The most

318

### computationally expensive task is hypocenter location, therefore we decided to utilize a grid search

319

### approach based on trace stacking, a strategy which does not require picking of the first arrivals,

320

### and leverages precomputed traveltime tables. This approach relies on discretization of the

321

### subsurface model and is a purely data-driven stacking approach for computing a source location

322

### image.

323

### The DAS data are first pre-processed (Figure 3). Our methodology closely follows

324

### hypocenter location algorithms derived from Kirchhoff or diffraction-stack migration of seismic

325

manuscript submitted to _JGR: Solid Earth_

### wavefield back to the source location and origin time (e.g. Zeng et al., 2014; Li et al., 2018, 2020;

326

### Gajewski & Tessmer, 2005; Gajewski et al., 2007; Zhebel & Eisner, 2015; Beckel et al., 2021).

327

### Our near-vertical receiver geometry doesn’t constrain the absolute horizontal location of the

328

### microseismic events. Therefore we characterize the locations in a 2D plane spanning radial

329 distance from the vertical well (𝒙𝒙𝟎𝟎) and absolute depth (𝒛𝒛𝟎𝟎), the latter being significantly better 330

### constrained than would have been possible with a surface monitoring array. We discretize the 2D

331 plane into square of grid nodes, referred to as image points. For each gridpoint (𝒙𝒙𝟎𝟎, 𝒛𝒛𝟎𝟎) as a 332 possible source location, we stack the characterstic functions 𝑨𝑨𝒊𝒊 for waveforms recorded at 𝑵𝑵 DAS 333

### channels along the travel-time moveout with an additional time shift corresponding to the currently

334 evaluated origin time 𝒕𝒕𝟎𝟎: 335

𝑰𝑰(𝒙𝒙𝟎𝟎, 𝒛𝒛𝟎𝟎, 𝒕𝒕𝟎𝟎) =  𝑨𝑨𝒊𝒊 𝒕𝒕𝟎𝟎 + 𝝉𝝉𝑺𝑺 𝒊𝒊 (𝒙𝒙𝟎𝟎, 𝒛𝒛𝟎𝟎)

𝑵𝑵

𝒊𝒊=𝟏𝟏

336

where 𝐼𝐼(𝑥𝑥0, 𝑧𝑧0, 𝑡𝑡0) is the image function at the gridpoint (𝑥𝑥0, 𝑧𝑧0). 𝜏𝜏𝑆𝑆 𝑖𝑖 is the S-wave travel-time from 337

### the image point to channel 𝑖𝑖, pre-computed using a 1D velocity model derived from the well logs

338 at well 73-22. We use one the simplest form of 𝐴𝐴𝑖𝑖, i.e., an absolute value of the recorded waveform. 339

### The image function is computed for each grid node, and each potential origin time, resulting in a

340

### 3D matrix. The maximum value of the 3D image function corresponds to the most probable

341

### location of the event. We emphasize here that fidelity of sum-and-stack location approach is based

342

### on finding the S-wave traveltime moveout curve unique to a grid node and origin time combination

343

### that yields the highest value of image function. In Text S3 we show location benchmarking results,

344

### using approximations of the geometry of the observation well and a synthetic elastic forward

345

### model.

346

347

### **Figure 3** . Microseismic event preprocessing workflow. (a) Preprocessing sequence. (b) Raw data.

348

### (c) Spatially averaged data. (d) Bandpass-filtered data. (e) Common-mode filtered data.

349

### 3\.2.2 Local Magnitude, b-value and magnitude of completeness

350

### In this subsection we describe the estimation of local event magnitude, magnitude of completeness,

351

### and b-values for detected seismic events. From the above three parameters, only the local

352

### magnitude is estimated inside the real-time loop; magnitude of completeness and b-value are

353

manuscript submitted to _JGR: Solid Earth_

### calculated as part of batched post-processing. For local magnitude computation, we used the

354

### empirical relationship proposed by Yin et al. (2023a, 2023b):

355

log10 𝐸𝐸𝑖𝑖 𝑆𝑆 = 0.69𝑀𝑀 − 1.588 log10 𝐷𝐷𝑖𝑖 + 𝐾𝐾𝑖𝑖 𝑆𝑆 356

### where 𝐸𝐸 is the observed peak amplitude of DAS strain rate, 𝑀𝑀 is earthquake magnitude, 𝐷𝐷 is the

357 distance of the detected event to the DAS channel 𝑖𝑖, and 𝐾𝐾𝑖𝑖 is a site-specific term individual for 358 channel 𝑖𝑖. Due to the absence of any independent magnitude estimates required for calibrating 𝐾𝐾𝑖𝑖, 359 we assume 𝐾𝐾𝑖𝑖 to be zero. This assumption is a limitation at our particular site for _ML_ estimation; 360

### an alternative is the use of more sophisticated DAS magnitude estimation approaches such as the

361

### low-frequency algorithm recently introduced by Nayak et al. (2024) which should mitigate this

362

### challenge.

363

### Next, we use the event frequency-magnitude distribution to estimate magnitude of completeness

364

### and Gutenberg-Richer statistics a- and b- values that are a key input in seismic hazard estimates.

365

### Our b‐value estimates were determined based on two different assumptions regarding the

366

### maximum size of a confined rupture. First, we considered an unbounded maximum magnitude,

367

### consistent with the traditional Gutenberg–Richter (G‐R) relation, and calculate the b-value using

368

### the maximum likelihood method proposed by Aki (1965), with uncertainty quantified using the

369

### standard error approach outlined by Shi and Bolt (1982). Next, the magnitude distribution was

370

### modeled using a truncated Gutenberg–Richter distribution, as described in the finite‐volume

371

### framework by Dinske and Shapiro (2013). This approach assumes that ruptures are limited to the

372

### stimulated rock volume and cannot extend beyond it, thereby imposing a geometric constraint on

373

### their size (e.g., Bourne & Oates, 2020). The magnitude of completeness (Mc) was determined

374

### using the maximum curvature approach (Wiemer & Wyss, 2000). This method estimates Mc as

375

manuscript submitted to _JGR: Solid Earth_

### the magnitude bin from the non-cumulative frequency-magnitude distribution that contains the

376

### highest event frequency.

377

378

### **Figure 4** . Event locations from the real-time downhole-DAS system operating during Blue

379

### Mountain experiment. (a) Cross section representing event locations with respect to the

380

### observation well 73-22. Colors represent density of events at each grid point. (b) Image function

381

### for exemplar microseismic event. (c) Data-driven location uncertainty computed for event in (b).

382

### 3\.3 Seismic diffusivity

383

### In this subsection, we analyze the spatio-temporal evolution of seismicity associated with the

384

### cyclic injection cycles. The occurrence of injection-induced seismicity is typically characterized

385

### by an increase in the radial distances of microseismic event locations from the injection point with

386

### increasing time. The onset of seismicity as a function of space and time can be approximated by

387

### three-dimensional surface, i.e. a triggering front, propagating away from the injection point

388

### (Shapiro et al., 2006; Barthwal & Van Der Baan, 2019, Hagenson & Rajaral, 2021; Delepine et

389

### al., 2004; Shapiro, 2015; Shapiro et al., 1997, 2002). The triggering front marks the arrival of pore-

390

### pressure perturbations that propagate through the subsurface following the well-known diffusion

391

### equation. Assuming an homogeneous and isotropic subsurface, the onset time of seismicity 𝑡𝑡 since

392

### the beginning of injection at a distance 𝑟𝑟 from the injection point can be approximated by

393

### 𝑟𝑟 = √4𝜋𝜋𝐷𝐷𝑡𝑡

394

### where 𝐷𝐷 is seismic diffusivity expressed in

𝑚𝑚 ²

𝑠𝑠 and is considered to be a proxy for hydraulic 395

### diffusivity. To more accurately capture the spatial relationship between seismicity and injection,

396

### we estimate the distance of each event from the injection well directly, rather than approximating

397

### it using distance from the monitoring well. The relative perpendicular orientation of the vertical

398

### monitoring well to the injection well means it is particularly insensitive to detecting radial changes

399

manuscript submitted to _JGR: Solid Earth_

### relative to the horizontal injector. For this reason, we use only the relative vertical locations of

400

### events to improve spatial accuracy. We then analyze the variation in event distance from the

401

### injection well as a function of time during the flexible injection cycles.

402

### **4 Results**

403

### The real-time monitoring system ran close to continuously for 2 months (between March 15 and

404

### May 16 2023) with only one downtime related to an extended power outage. In total, we detected

405

### and located ~13,500 events over this time interval. All partial results described in the Monitoring

406

### architecture subsection were exported to the cloud in real-time as rough picks, locations,

407

### magnitudes, and hourly seismicity reports. We note that the true number of events may be higher,

408

### and the final catalog corresponds to the events for which the image function maximum in space

409

### and time exceeded a threshold that was determined empirically on trial and error basis and meant

410

### to balance the number of detected events and number of the false detections.

411

### 4\.1 Overall spatial distribution of microseismicity

412

### Figure 4a shows a summary of microseismic event locations, in which dots correspond to the

413

### source grid coordinates and the colors indicate the number of microseismic events occurring at the

414

### grid points. The center of the microseismic cloud is located approximately at a depth of 2720

415

### meters, approximately 800 meters from the borehole. It also approximately corresponds to the area

416

### where the highest number of events occurred during the monitoring period (the red blob in Figure

417

### 4a). Despite the limitation of being able to resolve only the radial distance from the monitoring

418

### well and absolute depth, the microseismic cloud shown in Figure 4a aligns with event locations in

419

### close proximity to the observational well 73-22 as reported by Norbeck and Latimer (2023),

420

### consistent with their microseismic analysis accurately representing the outline and geometry of the

421

### Stimulated Reservoir Volume (SRV).

422

423

### **Figure 5** . Seismicity recorded during the stimulation and crossflow tests at the Blue Mountain

424

### EGS pilot. (a) Microseismic catalog recorded between March 15 and May 16 2023, showing the

425

### number of events detected in 1-hour intervals (gray bars) alongside downhole pressure

426

### measurements from pressure gauge at the Well 73-22 (black line), production rate data (red line),

427

manuscript submitted to _JGR: Solid Earth_

### and injection rate data (blue lines). Dashed black lines indicate the duration of the crossflow test

428

### and a series of dispatchable load cycles, while black arrows mark pressure peaks associated with

429

### individual cycles. (b) Frequency-magnitude distribution of the events shown in (a), with

430

### cumulative (gray bars) and non-cumulative (pink dots) magnitude–frequency distributions.

431

### Gutenberg-Richter fits are displayed as a solid blue line (Aki, 1965) and a dashed blue line

432

### (Shapiro et al., 2013). The dashed black line represents the magnitude of completeness. (c)

433

### Magnitudes of events shown in (a), represented by varying symbol sizes and colors, plotted with

434

### the smoothed number of events (white line) over 2-hour intervals. The timing of the largest

435

### recorded micro-earthquake (magnitude 0.45) is marked by a vertical black line.

436

### 4\.2 Overall temporal distribution of microseismicity

437

### In Figure 5, we present a summary of the seismic activity recorded during the entire experiment

438

### including the crossflow production tests and flexible injection cycles along with the pressure

439

### measurements obtained from the downhole gauge positioned behind the casing in the 73-22 well

440

### (away from the two horizontal wells, but within the stimulated reservoir volume). Figure 5a

441

### highlights one of the primary observations of this study: the pressure-dependent behavior of

442

### injection-induced seismicity throughout the entire monitoring period. The highest seismicity rates

443

### in the experiment, up to ~60 events per hour, were recorded during the stimulation conducted at

444

### production well 34-22, coinciding with the highest subsurface fluid pressure. Following the

445

### stimulation, the seismicity rate gradually decreased as the pressure dissipated and stabilized to ~5

446

### events per hour. The seismicity rate slightly increased to ~10 events per hour with minor

447

### fluctuations following a minor increase in pressure during the crossflow production tests. During

448

### May 1-5, 2023, a series of 5 dispatchable cycles (denoted with black arrows in Figure 5a) involving

449

### changes in production rate led to cyclical but overall increasing pressures with a corresponding

450

### increase in the seismicity rate. Following the conclusion of the tests, the seismicity rate gradually

451

### decreased as the pressure dissipated. The relationship between seismicity and the presumed

452

### pressure diffusion during these cycles is discussed in the subsequent sections.

453

454

### 4\.3 Frequency-magnitude distribution

455

### The frequency-magnitude distribution of all detected microseismicity is depicted in Figure 5b,

456

### with the largest and smallest detected events measuring ~ –1.3 and ~ +0.45, respectively. The

457

### cumulative distribution shown in Figure 5b was utilized to estimate the magnitude of completeness

458

### and the b-value. The b‐value was calculated using two approaches with distinct assumptions about

459

### the maximum rupture size. When an unbounded maximum magnitude was assumed, the b‐value

460

### was determined to be 1.732. In contrast, when the magnitude distribution was modeled using a

461

### truncated Gutenberg–Richter distribution, the b‐value was calculated to be 1.617, reflecting the

462

### influence of geometric constraints on the rupture size. Further studies should be dedicated to

463

### refining these parameters, given the implications for hazard estimation. The estimated b-values are

464

### considerably greater than the tectonic average for Nevada ~ 0.84 (Trugman, 2024) and the b-value

465

### of ~0.94 observed during a highly active tectonic swarm in 2008 in eastern Nevada that also

466

### showed evidence of pore-pressure diffusion (Ruhl et al., 2016). The value is also higher than the

467

### b-value of ~1.6 documented by Kwiatek et al. (2019) during EGS experiments in deep crystalline

468

### rocks in Finland and is higher than most of the EGS sites documented in Li et al. (2024b) including

469

manuscript submitted to _JGR: Solid Earth_

### Utah FORGE. The steeper slope observed for events with magnitudes ≳–0.2 may suggest either

470

### insufficient recording time or inherent limitations in generation of relatively larger magnitude

471

### events due to geological or tectonic constraints (e.g., Lellouch et al., 2020).

472

473

### 4\.4 Seismic Diffusivity of cyclic injection cycles

474

### The summarized monitoring results (Figure 5a) in the subsection 4.1 showed consistent correlation

475

### between injection pressure changes and seismicity throughout the experiment. With event

476

### locations estimated and a narrower time interval singled out from the microseismic catalog, we

477

### conducted a more detailed spatio-temporal characterization of the microseismic cloud. Figure 6

478

### presents a spatiotemporal analysis of microseismicity recorded during the five dispatchable load

479

### cycles of the Blue Mountain EGS experiment, highlighting the evolution of event timing, distance

480

### from the well, and magnitude in relation to pressure, production, and injection trends (Figure 6a–

481

### e).

482

### The red line in Figure 6a represents the estimated triggering front, based on the onset time of

483

### induced seismicity as a function of distance using vertically projected event locations and a single

484

### best-fit seismic diffusivity value (Equation 2). The area below the triggering front describes the

485

### parabolic envelope, which appears to accurately represent the upper bound of the majority of

486

### events detected during flexible EGS operations. The diffusivity parameter corresponding to

487

### triggering front in Figure 6a is 0.43 m²/s.

488

### 4\.5 Microseismic event magnitudes

489

### The largest event detected during our experiment was of magnitude ~0.45 with ~80 events greater

490

### than magnitude > 0 (Figure 5b). The US Geological Survey’s NEIC catalog contains no seismicity

491

### within ~20 km of the study area during the period of injection or after the end of the experiment

492

### until July of 2024. This is not surprising as the study area is sparsely instrumented with the closest

493

### permanent seismic station being >50 km away (Hellweg et al., 2020; ds.iris.edu/mda/NN/, last

494

### accessed June 2024). Our magnitude estimates are consistent with the upper bound imposed by

495

### the average magnitude of completeness of ~1.8 for the regional seismic catalog in Nevada

496

### (Trugman, 2024).

497

About ~1.35x10 ⁵ m ³ and ~1.07x10 ⁵ m ³ of fluid volume were injected and produced, respectively, 498

### during the crossflow tests and flexible cycles from April 9 to May 16 (Norbeck and Latimer,

499

### 2023). McGarr (2014) proposed a simple relationship between the injected fluid volume and the

500

### maximum seismic moment or magnitude of the seismic events induced under the assumptions that

501

### the rock mass is brittle and saturated, and the induced seismic events are localized to the region

502 weakened by the pore pressure increase. Assuming a rigidity modulus of ~3.2x10 ¹⁰ Pa, we obtain 503

### magnitudes of ~4.4 and ~3.9 assuming injected and residual fluid volumes, respectively, which

504

### are significantly larger than the observed maximum magnitude of ~0.45. Shapiro et al. (2011)

505

### suggested an alternate model in which the maximum magnitude of the induced seismic event is

506

### geometrically limited by the dimensions of the stimulated rock mass. We assume an average stress

507

### drop of 3 MPa and constant C~1 in the formulation of equation 6 in Shapiro et al. (2011). For the

508

### range of length scales of the seismicity cloud ~0.2 to 1 km, we get magnitudes of ~2.9 to 4.3,

509

manuscript submitted to _JGR: Solid Earth_

### exceeding the observed value. The scarcity of larger magnitude events could be possibly due to

510

### the absence of large asperities in the causative faults. In either scenario, simple relationships for

511

### linking fluid volume to peak magnitude moment appear to overestimate maximum event size for

512

### this dataset.

513

### 4\.6 Evolving Seismic Response

514

### To better understand the seismicity associated with the crossflow test and flexible operations, we

515

### analyze key seismic parameters for events above the magnitude of completeness. Specifically, we

516

### examine the seismogenic index and cumulative seismic moment. The seismogenic index, which

517

### quantifies earthquake productivity per unit of fluid injection (Shapiro et al., 2010, Dinske and

518

### Shapiro, 2013), is calculated using a maximum likelihood approach for each new event, tracking

519

### its evolution over time and injected volume (Schulz et al., 2018). Additionally, we calculate the

520

### cumulative seismic moment and fit its progression to two models: one predicting proportionality

521

### to 2G∙V (McGarr, 2014) and another to γ×V^(3/2) (Galis et al., 2017), using linear regression.

522

### Both metrics reveal similar trends (Fig. 7). Seismic activity is pronounced during the crossflow

523

### test but diminishes notably at the onset of flexible operations, transitioning to a weaker response.

524

### While the seismogenic index indicates an overall two-order-of-magnitude reduction in seismic

525

### productivity, it shows a steady increase following the start of flexible operations. In contrast,

526

### cumulative seismic moment results suggest initially low productivity, aligning with the

527

### seismogenic index's trend of a gradual increase in seismicity during flexible operations.

528

### Despite the relatively small seismic response at Blue Mountain (normalized by injected volume),

529

### the observed increase over time suggests that seismicity development is tied to fluid injection into

530

### the subsurface rather than intrinsic tectonic activity in the region. While seismic responses are

531

### often stable, some studies have reported time-dependent increases (Bentz et al., 2020; Rodríguez-

532

### Pradilla et al., 2022). Determining whether the seismic response is stable or evolving is crucial for

533

### management, as such non-stationary behavior could challenge initial hazard assumptions.

534

### Observed changes have been linked to fluid pressure migration activating distant fault patches

535

### (Bentz et al., 2020), fault valving unlocking fault segments (Zhu et al., 2020), transitions to

536

### runaway rupture (Rodríguez-Pradilla et al., 2022), or shifts from aseismic slip to stick-slip ruptures

537

### (Eyre et al., 2019). At Blue Mountain, distinguishing these possibilities will likely require longer

538

### duration analysis.

539

### **5 Discussion**

540

### 5\.1 A practical outlook on real-time monitoring of the dispatchable cycles

541

### To date, it has been demonstrated that EGS seismicity is largely a function of fluid injection and

542

### withdrawal (e.g., Majer et al., 2007). Protocols for induced seismicity (Majer et al., 2012)

543

### recognize this as a positive feature, indicating that balancing the injection and fluid withdrawal

544

### could potentially control the seismicity by preventing long-term pressurization of critically

545

### stressed features at a distance from the EGS facility. Two features of EGS injection-induced

546

### seismicity (Majer & Peterson, 2005) are particularly relevant for this study: (i) as time progresses

547

### after injection, the EGS system reaches equilibrium and seismicity decreases, and (ii) the initial

548

### level of seismicity is smaller when the injection rate is varied. Both phenomena allow us to explain

549

manuscript submitted to _JGR: Solid Earth_

### the main spatio-temporal features of seismicity related to dispatchable cycles (Figure 6): pressure-

550

### dependent behavior of seismicity with spikes in the number of events correlating in time and

551

### number with charging and discharging cycles, and a lower maximum number of events during

552

### flexible operations compared to the high level of events during earlier stimulation activities.

553

### One ongoing research question is whether seismic diffusivity can accurately estimate the effective

554

### hydraulic diffusivity of the injection formation (Haagneson & Rajaram, 2021). This is based on

555

### the observation that seismicity is anticipated to propagate at the threshold triggering pressure,

556

### potentially outpacing effective hydraulic diffusivity in heterogeneous media, especially in

557

### fractured zones. Regardless of the positive verification of this hypothesis, the spatio-temporal

558

### distribution of microseismic events detected during flexible operations from our workflow renders

559

### a dynamically evolving propagation front when projected on the r-t plot (Figure 6b). Under the

560

### simplifying assumption of an isotropic and homogeneous porous medium (Shapiro et al., 2006),

561

### we applied a linear diffusion framework and approximated the dynamics of the microseismic cloud

562

### as a 1D propagating front. To capture spatial relationships within this framework, we compute

563

### event distances relative to the horizontally oriented injection well and incorporate the vertical

564

### distribution of events. While we cannot directly verify the link between our data-driven seismic

565

### diffusivity and the hydraulic properties of the injection formation, the observed spatiotemporal

566

### evolution of seismicity under flexible injection cycles shows characteristics similar to those

567

### reported in hydraulic fracturing contexts. The estimated diffusivity of approximately 0.43 m²/s

568

### slightly exceeds, but is broadly consistent with, the range of theoretical hydraulic diffusivity values

569

### reported for fault damage zones in the Blue Mountain area (0.08–0.33 m²/s; Guo et al., 2021),

570

### suggesting the presence of a highly permeable or fractured formation.

571

### From the induced seismicity mitigation standpoint, the main challenge is to optimize production

572

### while preventing large seismic events (e.g., Majer & Peterson, 2005). In conjunction with the

573

### feasibility of the Blue Mountain real-time monitoring system to provide information on the spatio-

574

### temporal evolution of microseismicity correlating with pressure changes, the availability of this

575

### information opens the door to dynamic feedback algorithms for controlling injection rate. If

576

### perfected, such approaches offer the potential to increase the safety of EGS operations.

577

578

### Figure 6. The spatiotemporal analysis of seismicity recorded during a series of dispatchable

579

### cycles. (a) Event occurrence time versus distance (r-t) plots of seismicity, overlaid with the

580

### downhole gauge pressure curve (blue line). The dots represent the projection of event

581

manuscript submitted to _JGR: Solid Earth_

### hypocenters using vertical locations only during the flexible operation of the EGS, with

582

### colors indicating elapsed time since the start of dispatchable cycle operations. Events used

583

### for diffusion model fitting are marked with green circles. The red line indicates the best-fit

584

### synthetic diffusion curve, with diffusivity (D) value displayed at the top of the curve.

585

### Dashed black lines show the lower and upper bounds of diffusivity values, accounting for

586

### location uncertainty. Roman numerals I-III correspond to cycles with restricted production,

587

### while IV-V denote cycles where production was fully halted during injection and resumed

588

### unrestricted flow after 12 hours. (b) Event occurrence time versus magnitude, shown

589

### alongside the downhole pressure curve. Magnitudes are depicted with varying symbol sizes

590

### and colors. (c-e) Event distributions (gray bars) juxtaposed with the smoothed number of

591

### events (black line) and plotted against the downhole pressure curve (c), production rate

592

### data (d), and injection rate curve (e).

593

### 5\.2 Qualitative interpretation of time-delay between increase in seismicity and cyclic

594

### injection cycles

595

### In flexible geothermal operations, restricted production limits fluid extraction based on grid

596

### demand or economic factors, helping balance energy supply by reducing output when demand is

597

### low or when other renewable sources (e.g., solar, wind) are sufficient. In contrast, unrestricted

598

### production operates at maximum flow capacity, maximizing electricity generation when demand

599

### is high or when grid conditions favor full production, allowing continuous extraction without

600

### constraints. The series of load-following dispatchability tests comprised a total of 5 cycles: three

601

### with restricted production, followed by two where production was entirely halted during injection

602

### and allowed to flow unrestricted after 12 hours. In the final two cycles, where production was left

603

### unrestricted, we observed a distinct time delay in seismicity elevation with respect to pressure

604

### increase (denoted with a black arrow in Figure 5a). Based on the data shown in plot 6a, the time

605

### delay between seismicity within a single cycle and pressure increases with time (note the

606

### increasing delay in the ascending part of seismicity denoted for cycle IV in Figure 6a), and seems

607

### to be partially controlled by the slope of the pressure curve. For this reason, seismicity appears to

608

### be driven by both the value of pressure at the given time and the injection rate (increase of injection

609

### over time); for the largest cycles, when pressure starts to approach the maximum, the slope of the

610

### pressure curve decreases, so the seismicity still rises, but at a slower rate.

611

### As described in the Results section, the number of detected events per hour correlates with

612

### injection pressure throughout the entire duration of a series of dispatchable cycles. However, it is

613

### important to note that the observed increase in seismicity over time (i.e., the slope of the black

614

### curve in Figure 6c) appears to be influenced by the corresponding increase in pressure (slope of

615

### the blue curve in Figure 6c). This observation is based on data-driven features specific to this study

616

### and should not be interpreted universally. Further investigation is required to fully understand the

617

### relationship between injection pressure and seismicity in this case, potentially through use of a

618

### more sophisticated hydromechanical model to understand pressure state at distance. Nonetheless,

619

### the findings may provide some insight into potential strategies for proactively mitigating induced

620

### seismicity, such as reducing injection rate before reaching the planned maximum production.

621

### Additionally, while it may be reasonable to increase injection rate at the beginning of dispatchable

622

### load cycles to potentially induce more low-magnitude events early on and fewer higher-magnitude

623

### events closer to maximum production, without a detailed analysis of maximum magnitude

624

### variations during the experiment, this remains speculative. However, the record-breaking

625

manuscript submitted to _JGR: Solid Earth_

### magnitudes (i.e., events that represent a new largest magnitude up to that time), when juxtaposed

626

### with the cumulative seismic moment release (Figure 7c), tend to appear at the end of flexible

627

### cycles, which may provide a slight indication of this trend.

628

### Observations of seismicity for the initial cycles (cycles I-III in Figure 6) exhibit more complex

629

### behavior due to production not being entirely halted. Particularly, we note inter-cycle overlap i.e.

630

### the increase in seismicity from one peak being affected by ongoing seismicity effects from the

631

### previous one. Further analysis of cycles with restricted production should rely on inspecting the

632

### microseismic catalog over shorter time spans (equivalent to the length of a single cycle) using

633

### event binning in shorter bins. This observation is emphasized by the smoothed number of events

634

### curve (black line in Figure 6c) showing more seismicity peaks than production cycles.

635

### Juxtaposing the observations of seismicity between cycles with restricted and unrestricted

636

### production, the latter allows for more accurate tracking of their seismicity in real-time, due to the

637

### apparent minimal interference of seismicity between neighboring cycles. From the perspective of

638

### future IS mitigation programs, we highlight the following observation relevant for the flexible

639

### EGS context: While current results hint at a possible link between the evolution of seismicity

640

### during flexible operations of EGS and the time interval between subsequent cycles, and that

641

### minimizing the production levels between two consecutive cycles can lead to achieving the

642

### equilibrium of the microseismic system (i.e., to the pre-cyclic-injection state), this study does not

643

### undertake a systematic evaluation of the effects of varying time intervals between injection cycles

644

### on seismicity evolution. Further research is needed to test whether resetting the system between

645

### cycles would allow the real-time monitoring system to provide ad-hoc feedback on seismicity

646

### related exclusively to the current operations.

647

### 5\.3 b-value from real-time analysis: fault reactivation indicator or magnitude predictor

648

### From the standpoint of induced seismicity mitigation, one of the primary expectations of a real-

649

### time monitoring system is to furnish reliable metrics that represent the risk of fault reactivation.

650

### The two main metrics are the increase in microseismicity relative to injection rate and a decrease

651

### in b-values. While we discussed the increase of microseismicity approach in the preceding

652

### subsection, here we concentrate on the b-value approach and the context in which the approximate

653

### nature of calculating this parameter does not impede its utility in a real-time monitoring system.

654

### Accurate estimation of b-values is a widely discussed topic in seismology (see Godano & Petrillo,

655

### 2023 and references therein) but there is consensus that the b-value quantifies the relative

656

### frequency of large versus small events and can offer insights into temporal variations of stress on

657

### different fault zones (e.g., Amitrano et al., 2003; Scholz, 2015). Calculations of b-values are prone

658

### to inherent biases, primarily due to irregular behavior of the detection threshold, resulting in

659

### earthquake catalogs incomplete with small events that slipped under the detection threshold. One

660

### common approach to address this issue is to limit the evaluation of b-values to events with a

661

### magnitude greater than a specified threshold, most commonly equal to the magnitude of

662

### completeness (Mc). However, this approach requires using a restricted number of earthquakes

663

### within each analyzed space-time region, which in turn generates further biases related to statistical

664

### fluctuations that can mask variations of b-values (Shi & Bolt, 1982). For a more comprehensive

665

manuscript submitted to _JGR: Solid Earth_

### overview of b-value and magnitude of completeness estimation see Geffers et al. (2022) and

666

### Mignan et al. (2012) respectively.

667

### While thresholding the magnitude of completeness allows for a reduction in bias during

668

### computation of b-values, selecting the magnitude of completeness faces its own challenges,

669

### particularly when using short recording periods incorporating small events. For instance,

670

### restricting the number of events used for improved b-value estimates requires using only events

671

### from homogeneous regions of the network for which the same detection threshold is valid (e.g.,

672

### Wiemer, 2000). In other words, as long as different spatial nodes under the area of investigation

673

### are characterized by the same detection threshold, then all events can be used for Mc estimation.

674

### A particular challenge in our case is the limited recording geometry (DAS in a single vertical well)

675

### which guarantees that more distal regions of the recording volume have a different Mc than events

676

### close to the well.

677

### As explained in the Methods section, we estimated b-values based on frequency–magnitude

678

### distributions using two different modeling assumptions regarding the maximum possible

679

### earthquake size. First, we applied the maximum likelihood method (Aki, 1965) under the

680

### traditional Gutenberg–Richter (G–R) formulation, assuming no upper bound on magnitude.

681

### Uncertainty in this estimate was assessed using the standard error approach by Shi and Bolt (1982).

682

### Second, we employed a truncated G–R model following the finite-volume framework (Dinske &

683

### Shapiro, 2013), which constrains the maximum magnitude based on the volume of the stimulated

684

### rock, consistent with the concept of geometrically confined ruptures (e.g., Bourne & Oates, 2020).

685

### The magnitude of completeness (Mc) was determined using the maximum curvature method

686

### (Wiemer & Wyss, 2000), which identifies Mc as the magnitude bin with the highest frequency in

687

### the non-cumulative distribution. These data-driven approaches reduce the tradeoff between b-

688

### value and Mc by selecting a subset of the catalog most consistent with the G–R scaling, supporting

689

### the assumption that induced seismicity at fluid injection sites can follow the same statistical

690

### patterns as tectonic earthquakes (van der Elst et al., 2016).

691

### Nevertheless, due to using an artificially created catalog, the presented b-value and magnitude of

692

### completeness are only correct with respect to the selected processing framework. Monitoring a

693

### spatially constrained area using the same detection threshold throughout the whole experiment and

694

### providing the approximate estimate of b-value has specific implications for its specific use in the

695

### real-time IS mitigation context. While using the b-value derived in this study to make forecasts of

696

### the expected event magnitudes during injection-induced seismicity is not recommended due to

697

### inherent biases in these estimates, the temporal variations of b-value may serve as an indicator for

698

manuscript submitted to _JGR: Solid Earth_

### fault reactivation identification, relying solely on the relative decrease of b-values (e.g., Maxwell

699

### et al., 2009a; Verdon and Budge, 2018; Kettlety et al., 2019).

700

701

### Figure 7. Injection parameters as a function of disposed volume. (a) Number of earthquakes above

702

### the detection threshold (-0.8) versus cumulative injection volume. Data from the Blue Mountain

703

### EGS operations, spanning from April 10 to the end of the experiment on May 16, are compared to

704

### the best-fit line (black). The fit quality is quantified using the coefficient of determination (R²),

705

### indicating the goodness-of-fit between the observed data and the expected trend. (b) Seismogenic

706

### index and (c) cumulative seismic moment plotted as a function of injected volume with

707

### McGarr/Galis best fits (dashed and dotted line, respectively). The occurrence times of new record-

708

### breaking magnitudes are indicated by red x’s.

709

### 5\.4 Real-time feedback vs accuracy tradeoff

710

### While mapping microseismic events serves as a valuable tool for reservoir management, these

711

### small events may also be regarded with concern, particularly if felt by communities located near

712

### geothermal fields (Majer et al., 2007). Thus, assuming that real-time DAS-based monitoring

713

### accurately represents the true state of seismicity, the resulting microseismic catalog reflects the

714

### dual nature of this information: (i) associated hazard and (ii) feedback about the reservoir system.

715

### The strength of this connection, i.e., how well the real-time derived catalogs reflect both

716

### parameters, is determined by the quality of the microseismic catalog. Reiterating the main key

717

### points of the ‘Data and Method’ section, the main part of the methodological focus of this study

718

### was to “win the race against the clock”, i.e., fit the entire processing flow within the time window

719

### between two consecutive data writes. In this study, we used a relatively simple processing

720

### approach which prioritized computational efficiency over the accuracy of the result. Leaving aside

721

### the explanation of each individual processing choice, we highlight the optimization of the most

722

### computationally intensive step – location. The main optimization step is computing the travel-time

723

### tables outside of the real-time monitoring loop, thus removing the need for recomputing travel

724

### times for each new data panel. Another speed-up factor is related to the discretization of the grid

725

manuscript submitted to _JGR: Solid Earth_

### search used for location (see details of discretization in the Location subsection in the Data and

726

### Monitoring Architecture section).

727

### Despite the above shortcomings, we suggest that the accuracy of the presented location results is

728

### sufficient to provide an approximate image of the SRV which constrains an outline of the gross

729

### treatment dimensions (e.g., Rutledge & Phillips, 2003; Maxwell et al., 2009b) and graphically

730

### illustrate the dominant feature of the spatiotemporal evolution of the microseismic cloud during

731

### time intervals of main interest: stimulation of the 34-22 production well and series of dispatchable

732

### load cycles. On the other hand, the presented results are not accurate enough for the detailed

733

### characterization of the SRV, and in turn making quantitative summaries about production

734

### performance, as providing only depth and distance makes it difficult to estimate the SRV.

735

### However, from the standpoint of the initial expectations posed on our real-time system, and

736

### considering the early stage of DAS-based monitoring in the geothermal sector (e.g., Dadi et al.,

737

### 2024), the performance is satisfactory. Particularly, as shown in Figure 6b, the real-time feedback

738

### allows for quantification of microseismic response of the reservoir at varying injection rates, and

739

### thus may allow operators to make informed modifications to their injection programs (e.g., Clarke

740

### et al., 2019; Kwiatek et al., 2019) based on the increase of seismicity rates or b-value variations.

741

### Specifically, these decisions should aim towards adjusting two real-time microseismic

742

### observables: (i) decreasing event count and/or cumulative seismic moment and (ii) increasing the

743

### time delays between pressure curves and the ascending part of the number of events plots.

744

745

### **6 Conclusions**

746

### Enhanced geothermal systems, initially viewed as a baseload energy production resource, have the

747

### potential to fill a wide range of niches in the electricity system by enabling flexible operations

748

### (load-following generation and long-duration energy storage). The seismicity generated by these

749

### flexible, often cyclic, EGS operations have not been heavily studied. We have quantified the

750

### previously uninvestigated seismicity of flexibly operating EGS using real-time fiber-optic based

751

### monitoring system. Leveraging the ultra-dense spatio-temporal sampling of distributed acoustic

752

### sensing, and an edge computing approach we developed the real-time microseismic workflow

753

### which performs complete microseismic processing sequence including (i) event detection, (ii)

754

### location, and (iii) magnitude estimation in the minute interval between sequential file writes. We

755

### continuously ran this workflow during the EGS pilot test of a flexible operations at Blue Mountain

756

### and provided real-time characterization of the seismicity associated with crossflow production test

757

### and a series of dispatchable cycles simulating flexible EGS operations. The resulting microseismic

758

### catalog shows pressure-dependent behavior of seismicity, consistent throughout the production

759

### well stimulation, crossflow test and a series of dispatchable load cycles.

760

### We verified that each dispatchable load cycle generates an individual peak in seismicity, and the

761

### number of detected events per hour rapidly levels off to an initial equilibrium after each cycle.

762

### Leveraging the concept of a triggering front, commonly used to characterize the spatio-temporal

763

### behavior of injection-induced seismicity, we found that the vertical propagation of the

764

### microseismic cloud during the 7-day period of flexible operations can be approximated by a linear

765

### diffusion equation. This analysis is based on vertical event locations only, and the resulting

766

### diffusivity values associated with the propagating fronts are consistent with those expected for

767

manuscript submitted to _JGR: Solid Earth_

### fractured zones, as indicated by previous synthetic studies conducted in the Blue Mountain

768

### geothermal area. Qualitative observation of the time-delay in seismicity elevation with respect to

769

### pressure increase was interpreted as likely related to pressure diffusion to fracture system

770

### boundary. Our results suggest that leveraging DAS and edge computing enables to track pressure

771

### dependent behavior of seismicity concurrently to the flexible operations of EGS systems.

772

### Using this real-time monitoring system, we studied several aspects of induced seismicity related

773

### to the flexibly operating EGS. Together with established diffusive-type behavior of microseismic

774

### clouds recorded during cyclic injections, we argue that the presented real-time processing

775

### framework and catalog highlight the potential of DAS-based monitoring for use in induced

776

### seismicity monitoring and reservoir management in the context of EGS systems.

777

### **Acknowledgments**

778

### Primary support for the Blue Mountain EGS pilot was provided by the Department of Energy,

779

### ARPA-E office under grant OPEN 1604. M. Chamarczuk and J. Ajo-Franklin would also like to

780

### thank the Air Force Research Laboratory (AFRL) for support of components within the real-time

781

### processing framework.

782

783

### **Open Research**

784

### The real-time microseismic catalog, location data, diffusivity curves, and exemplary continuous

785

### DAS recordings from observation well 73-22 are available at (Chamarczuk & Ajo-Franklin, 2025).

786

787

### **References**

788

### Aki, K. (1965). Maximum likelihood estimate of b in the formula log N = a - bM and its

789

### confidence limits. Bulletin of the Earthquake Research Institute, University of Tokyo, 43, 237–

790

### 239\.

791

792

### Amitrano, D. (2003). Brittle‐ductile transition and associated seismicity: Experimental and

793

### numerical studies and relationship with the b value. Journal of Geophysical Research, 108(B1).

794

### https://doi.org/10.1029/2001jb000680

795

### Asanuma, H., Kumano, Y., Hotta, A., Schanz, U., Niitsuma, H., & Häring, M. (2007). Analysis

796

### of microseismic events from a stimulation at Basel, Switzerland, GRC Transactions, 31, 265–

797

### 269\.

798

### Augustine, C., Fisher, S. B., Ho, J., Warren, I., & Witter, E. (2023). Enhanced geothermal shot

799

### analysis for the Geothermal Technologies Office. https://doi.org/10.2172/1922621

800

manuscript submitted to _JGR: Solid Earth_

### Augustine, C., Ho, J., & Blair, N. (2019). GeoVision Analysis Supporting Task Force Report:

801

### Electric Sector Potential to Penetration. https://doi.org/10.2172/1524768

802

### Azzola, J., Thiemann, K., & Gaucher, E. (2023). Integration of distributed acoustic sensing for

803

### real-time seismic monitoring of a geothermal field. Geothermal Energy, 11(1).

804

### https://doi.org/10.1186/s40517-023-00272-4

805

### Bachrach, R., Ramani, K., Arindam Kanrar, Gupta, S., Sayed, A., Twynam, F., Busanello, G.,

806

### Raknes, E. B., Ivanov, Y., & Sagary, C. (2023). New wiggles from old cables: Data processing

807

### and imaging considerations. Geophysics, 88(6), WC199–WC208.

808

### https://doi.org/10.1190/geo2023-0115.1

809

### Baik, E., Chawla, K., Jenkins, J. D., Kolster, C., Patankar, N., Olson, A., Benson, S. M., & Long,

810

### J. C. (2021). What is different about different net-zero carbon electricity systems? Energy and

811

### Climate Change, 2, 100046. https://doi.org/10.1016/j.egycc.2021.100046

812

### Baisch, S., Koch, C., & Muntendam‐Bos, A. (2019). Traffic Light Systems: To What Extent Can

813

### Induced Seismicity Be Controlled? Seismological Research Letters, 90(3), 1145–1154.

814

### https://doi.org/10.1785/0220180337

815

### Barthwal, H., & Van Der Baan, M. (2019). Role of fracture opening in triggering

816

### microseismicity observed during hydraulic fracturing. Geophysics, 84(3), KS105–KS118.

817

### https://doi.org/10.1190/geo2018-0425.1

818

### Beckel, R., Lund, B., Eggertsson, G., & Juhlin, C. (2021). Comparing the performance of

819

### stacking-based methods for microearthquake location: a case study from the Burträsk fault,

820

### northern Sweden. Geophysical Journal International, 228(3), 1918–1934.

821

### https://doi.org/10.1093/gji/ggab437

822

manuscript submitted to _JGR: Solid Earth_

### Bentz, S., G. Kwiatek, P. Martínez-Garzón, M. Bohnhoff, and G. Dresen (2020), Seismic

823

### moment evolution during hydraulic stimulations, Geophys. Res. Lett., 47(5), e2019GL086185,

824

### doi:10.1029/2019GL086185

825

### Bosman, K., Baig, A., Viegas, G., & Urbancic, T. (2016). Towards an improved understanding

826

### of induced seismicity associated with hydraulic fracturing. First Break, 34(7).

827

### https://doi.org/10.3997/1365-2397.34.7.86051

828

### Buijze, L., Bijsterveldt, L., Cremer, H., Jaarsma, B., Paap, B., Veldkamp, J.G., Wassing, B., Van

829

### Wees, J., van Yperen, G., & ter Heege, J. (2019). Induced seismicity in geothermal systems:

830

### Occurrences worldwide and implications for the Netherlands, European Geothermal Congress

831

### 2019, Den Haag, The Netherlands, June 11-14.

832

### Bourne, S., & Oates, S. (2020). Stress-dependent magnitudes of induced earthquakes in the

833

### Groningen gas field. Journal of Geophysical Research: Solid Earth, 125(11), e2020JB020013.

834

### https://doi.org/10.1029/2020JB020013

835

### Cai, Z., Shize, W., Wei, L., Fei, L., Chong, W., Liuyi, M., & Qing, L. (2019). Application of

836

### Walkaway-VSP based on joint observation by DAS and geophones in the Tarim Basin,

837

### northwest China. (974–978). Paper presented at 89th SEG International Annual Meeting. San

838

### Antonio, TX: Society of Exploration Geophysicists. https://doi.org/10.1190/segam2019-

839

### 3214449\.1

840

### Cardiff, M., Lim, D. D., Patterson, J. R., Akerley, J., Spielman, P., Lopeman, J., et al. (2018).

841

### Geothermal production and reduced seismicity: Correlation and proposed mechanism. Earth and

842

### Planetary Science Letters, 482, 470–477. https://doi.org/10.1016/j.epsl.2017.11.037

843

manuscript submitted to _JGR: Solid Earth_

### Chamarczuk, M., & Ajo-Franklin, J. (2025). Open research data for manuscript about insights

844

### into seismicity from the Blue Mountain Experiment (Version 1) [Dataset]. OSF.

845

### https://doi.org/10.17605/OSF.IO/D65BA

846

### Clarke, H., Eisner, L., Styles, P., & Turner, P. (2014). Felt seismicity associated with shale gas

847

### hydraulic fracturing: The first documented example in Europe. Geophysical Research Letters,

848

### 41(23), 8308–8314. https://doi.org/10.1002/2014gl062047

849

### Clarke, H., Verdon, J. P., Kettlety, T., Baird, A. F., & Kendall, J. (2019). Real‐Time imaging,

850

### forecasting, and management of Human‐Induced seismicity at Preston New Road, Lancashire,

851

### England. Seismological Research Letters. https://doi.org/10.1785/0220190110

852

### Dadi, S., Norbeck, J., Titov, A., Payeur, T., Machovoe, S., Joern, K., & Chinaemerem, K.

853

### Microseismic Monitoring of a Horizontal EGS System: Case Study and State of the Art. (2024).

854

### Proceedings 49th workshop geothermal reservoir engineering. Stanford, CA: Stanford

855

### University, February 12-14, SGP-TR-227.

856

### Davatzes, N., Feigl, K., Mellors, R., Foxall, W., Wang, H., & Drakos, P. (2013). Preliminary

857

### Investigation of Reservoir Dynamics Monitored Through Combined Surface Deformation and

858

### Micro-Earthquake Activity: Brady's Geothermal Field, Nevada. Proceedings 38th workshop

859

### geothermal reservoir engineering. Stanford, CA: Stanford University, February 11-13, SGP-TR-

860

### 198\.

861

### Deichmann, N., & Giardini, D. (2009). Earthquakes induced by the stimulation of an enhanced

862

### geothermal system below Basel (Switzerland). Seismological Research Letters, 80(5), 784–798.

863

### https://doi.org/10.1785/gssrl.80.5.784

864

### Delépine, N., Cuenot, N., Rothert, E., Parotidis, M., Rentsch, S., & Shapiro, S. A. (2004).

865

### Characterization of fluid transport properties of the Hot Dry Rock reservoir Soultz-2000 using

866

manuscript submitted to _JGR: Solid Earth_

### induced microseismicity. Journal of Geophysics and Engineering, 1(1), 77–83. https://doi.

867

### org/10.1088/1742-2132/1/1/010

868

### Dinske, C., & Shapiro, S. A. (2013). Seismotectonic state of reservoirs inferred from magnitude

869

### distributions of fluid-induced seismicity. Journal of seismology, 17, 13-25.

870

### Distributed Acoustic Sensing in Geophysics. (2021). In Y. Li, M. Karrenbach, & J. B. Ajo‐

871

### Franklin (Eds.), Geophysical Monograph Series. Wiley. https://doi.org/10.1002/9781119521808

872

### Dyer, B., Schanz, U., Ladner, F., Häring, M., & Spillman, T. (2008). Microseismic imaging of a

873

### geothermal reservoir stimulation. Leading Edge, 27(7), 856–869.

874

### https://doi.org/10.1190/1.2954024

875

### EIA. (2021). Monthly energy review, April 2021 (Technical Report). Energy Information

876

### Administration. Retrieved from https://www.eia.gov/totalenergy/data/monthly/pdf/mer.pdf

877

### Ellsworth, W. L., Giardini, D., Townend, J., Ge, S., & Shimamoto, T. (2019). Triggering of the

878

### Pohang, Korea, earthquake (M w 5.5) by enhanced geothermal system stimulation.

879

### Seismological Research Letters, 90(5), 1844–1858. https://doi.org/10.1785/0220190102

880

### Eyre, T.S., Eaton, D.W., Garagash, D.I., Zecevic, M., Venieri, M., Weir, R., & Lawton, D.C.

881

### (2019). The role of aseismic slip in hydraulic fracturing–induced seismicity. Science Advances,

882

### 5(8), eaav7172. https://doi.org/10.1126/sci-adv.aav7172

883

### Fercho, S., Norbeck, J., McConville, E., Hinz, N., Wallis, I., Titov, A., Agarwal, S., Dadi, S.,

884

### Gradl, C., Baca, H., Eddy, E., Lang, C., Voller, K., & Latimer, T. (2023). Geology, state of

885

### stress, and heat in place for a horizontal well geothermal development project at Blue Mountain,

886

### Nevada. Proceedings 48th workshop geothermal reservoir engineering. Stanford, CA: Stanford

887

### University, February 6-8, SGP-TR-224.

888

manuscript submitted to _JGR: Solid Earth_

### Gajewski, D., & Tessmer, E. (2005). Reverse modelling for seismic event characterization.

889

### Geophysical Journal International, 163(1), 276–284. https://doi.org/10.1111/j.1365-

890

### 246x.2005.02732.x

891

### Gajewski, D., Anikiev, D., Kashtan, B., & Tessmer, E. (2007). Localization of seismic events by

892

### diffraction stacking. In SEG Technical Program Expanded Abstracts 2007 (pp. 1287–1291).

893

### Society of Exploration Geophysicists. https://doi.org/10.1190/1.2792738

894

### Galis, M., Ampuero, J.P., Mai, P.M., & Cappa, F. (2017). Induced seismicity provides insight

895

### into why earthquake ruptures stop. Science Advances, 3(12), eaap7528.

896

### https://doi.org/10.1126/sciadv.aap7528

897

### Geffers, G., Main, I., & Naylor, M. (2022). Biases in estimating b-values from small earthquake

898

### catalogues: how high are high b-values? Geophysical Journal International, 229(3), 1840–1855.

899

### https://doi.org/10.1093/gji/ggac028

900

### Godano, C., & Petrillo, G. (2023). Estimating the completeness magnitude mc and the b-values

901

### in a snap. Earth and Space Science, 10, e2022EA002540. https://doi.org/10.1029/2022EA002540

902

### Gonzalez, L. F., Aguiar, A. C., & Karplus, M. Data mining microseismicity associated to the

903

### Blue Mountain geothermal site. (2022). Proceedings 47th workshop geothermal reservoir

904

### engineering. Stanford, CA: Stanford University, February 7-9, SGP-TR-223.

905

### Grigoli, F., Cesca, S., Rinaldi, A. P., Manconi, A., Lopez-Comino, J. A., Clinton, J. F., et al.

906

### (2018). The November 2017 Mw 5.5 Pohang earthquake: A possible case of induced seismicity

907

### in South Korea. Science, 360(6392), 1003–1006. https://doi.org/10.1126/science.aat2010

908

### Guo, H., Brodsky, E. E., Goebel, T. H. W., & Cladouhos, T. T. (2021). Measuring fault zone and

909

### host rock hydraulic properties using tidal responses. Geophysical Research Letters, 48,

910

### e2021GL093986. https://doi.org/10.1029/2021GL093986

911

manuscript submitted to _JGR: Solid Earth_

### Haagenson, R., & Rajaram, H. (2021). Seismic diffusivity and The influence of heterogeneity on

912

### injection-induced seismicity. Journal of Geophysical Research: Solid Earth,126,

913

### e2021JB021768. https://doi. org/10.1029/2021JB021768

914

### Häring, M. O., Schanz, U., Ladner, F., & Dyer, B. C. (2008). Characterisation of the Basel 1

915

### enhanced geothermal system. Geothermics, 37(5), 469–495.

916

https://doi.org/10.1016/j.geothermics.2008.06.002 917

Horne, R., Genter, A., McClure, M., Ellsworth, W., Norbeck, J. and Schill, E., 2025. Enhanced geothermal 918

systems for clean firm energy generation. _Nature Reviews Clean Technology_ , pp.1-13. 919

### Johnson, C.W., Totten, E.J. & Bürgmann, R., 2016. Depth migration of seasonally induced

920

### seismicity at The Geysers geothermal field, Geophys. Res. Lett., 43(12), 6196–6204

921

### Karrenbach, M., Cole, S., Ridge, A., Boone, K., Kahn, D., Rich, J., Silver, K., & Langton, D.

922

### (2019). Fiber-optic distributed acoustic sensing of microseismicity, strain and temperature during

923

### hydraulic fracturing. Geophysics, 84(1), D11–D23. https://doi.org/10.1190/geo2017-0396.1

924

### Kettlety, T., Verdon, J. P., Werner, M. J., Kendall, J. M., & Budge, J. (2019). Investigating the

925

### role of elastostatic stress transfer during hydraulic fracturing-induced fault activation.

926

### Geophysical Journal International. https://doi.org/10.1093/gji/ggz080

927

### Kwiatek, G., Saarno, T., Ader, T., Bluemle, F., Bohnhoff, M., Chendorain, M., Dresen, G.,

928

### Heikkinen, P., Kukkonen, I., Leary, P., Leonhardt, M., Malin, P., Martínez‐Garzón, P.,

929

### Passmore, K., Passmore, P. R., Valenzuela, S. G., & Wollin, C. (2019). Controlling fluid-

930

### induced seismicity during a 6.1-km-deep geothermal stimulation in Finland. Science Advances,

931

### 5(5). https://doi.org/10.1126/sciadv.aav7224

932

### Lellouch, A., Lindsey, N. J., Ellsworth, W. L., & Biondi, B. (2020). Comparison between

933

### distributed acoustic sensing and geophones – Downhole microseismic monitoring of the FORGE

934

### geothermal experiment. Seismological Research Letters, 91(6), 3256–3268.

935

### https://doi.org/10.1785/0220200149

936

manuscript submitted to _JGR: Solid Earth_

937

### Lellouch, A., Schultz, R., Lindsey, N.J., Biondi, B.L., & Ellsworth, W.L. (2021). Low-

938

### magnitude seismicity with a downhole distributed acoustic sensing array – Examples from the

939

### FORGE geothermal experiment. Journal of Geophysical Research: Solid Earth, 126,

940

### e2020JB020462. https://doi.org/10.1029/2020JB020462

941

942

### Li, D., Huang, L., Zheng, Y., Li, Y., Schoenball, M., Verónica Rodriguez-Tribaldos, Ajo-

943

### Franklin, J., Hopp, C., Johnson, T., Knox, H., Blankenship, D., Dobson, P., Kneafsey, T., &

944

### Robertson, M. (2024a). Detecting fractures and monitoring hydraulic fracturing processes at the

945

### first EGS Collab testbed using borehole DAS ambient noise. Geophysics, 89(2), D131–D138.

946

### https://doi.org/10.1190/geo2023-0078.1

947

948

### Li, D., Huang, L., Li, Y., Zheng, Y. and Moore, J., (2024b). Seismic monitoring of EGS fracture

949

### stimulations at Utah FORGE (Part 1): Time-lapse variations of b-values and Shear-wave

950

### Splitting Rates of induced microearthquakes. _Geothermics_ , _120_ , p.103005.

951

952

### Li, L., Becker, D., Chen, H., Wang, X., & Gajewski, D. (2018). A systematic analysis of

953

### correlation‐based seismic location methods. Geophysical Journal International, 212(1), 659–678.

954

### https://doi.org/10.1093/gji/ggx436

955

### Li, L., Tan, J., Schwarz, B., Staněk, F., Poiata, N., Shi, P., et al. (2020). Recent advances and

956

### challenges of waveform‐based seismic location methods at multiple scales. Reviews of

957

### Geophysics, 58, e2019RG000667. https://doi.org/10.1029/2019RG000667

958

### Majer, E. L., Baria, R., Stark, M., Oates, S., Bommer, J., Smith, B., & Asanuma, H. (2007).

959

### Induced seismicity associated with enhanced geothermal systems. Geothermics, 36(3), 185–222.

960

### https://doi.org/10.1016/j.geothermics.2007.03.003

961

### Majer, E., Baria, R., & Fehler, M. (2005). Cooperative research on induced seismicity associated

962

### with enhanced geothermal systems. GRC Transactions, 29, 99–101.

963

manuscript submitted to _JGR: Solid Earth_

### Majer, E., Nelson, J. S., Robertson-Tait, A., Savy, J., & Wong, I. G. (2012). Protocol for

964

### Addressing Induced Seismicity Associated with Enhanced Geothermal Systems.

965

### https://doi.org/10.2172/1219482

966

### Majer, E.L., & Peterson, J.E. (2005). Application of microearthquake monitoring for evaluating

967

### and managing the effects of fluid injection at naturally fractured EGS sites. GRC Transactions

968

### 29, 103–107.

969

### Maxwell, S. C., Jones, M., Parker, R., Miong, S., Leaney, S., Dorval, D., D’Amico, D., Logel, J.,

970

### Anderson, E., & Hammermaster, K. (2009). Fault activation during hydraulic fracturing. SEG

971

### Technical Program Expanded Abstracts 2009. https://doi.org/10.1190/1.3255145

972

### Maxwell, S., Rutledge, J., Jones, R. S., & Fehler, M. (2010). Petroleum reservoir characterization

973

### using downhole microseismic monitoring. Geophysics, 75(5), 75A129-75A137.

974

### https://doi.org/10.1190/1.3477966

975

### Maxwell, S., Waltman, C., Warpinski, N., Mayerhofer, M., & Boroumand, N. (2009). Imaging

976

### seismic deformation induced by hydraulic fracture complexity. SPE Reservoir Evaluation &

977

### Engineering, 12(01), 48–52. https://doi.org/10.2118/102801-pa

978

### McClure, M. W., & Horne, R. N. (2011). Pressure transient analysis of fracture zone

979

### permeability at Soultz-sous-Forêts. GRC Transactions, 35, 1487.

980

### McGarr, A. (2014), Maximum magnitude earthquakes induced by fluid injection, J. Geophys.

981

### Res. Solid Earth, 119, 1008–1019, doi:10.1002/ 2013JB010597.

982

### Mignan, A. (2012). Functional shape of the earthquake frequency-magnitude distribution and

983

### completeness magnitude. Journal of Geophysical Research: Solid Earth, 117(B8).

984

### https://doi.org/10.1029/2012jb009347

985

manuscript submitted to _JGR: Solid Earth_

### Nayak, A., Correa, J. and Ajo‐Franklin, J., (2024). Seismic Magnitude Estimation Using Low‐

986

### Frequency Strain Amplitudes Recorded by DAS Arrays at Far‐Field Distances. _Bulletin of the_

987

### _Seismological Society of America_ , _114_ (4), pp.1818-1838.

988

### Norbeck, J., & Latimer, T. (2023). Commercial-Scale demonstration of a First-of-a-Kind

989

### enhanced geothermal system. EarthArXiv (California Digital Library).

990

### https://doi.org/10.31223/x52x0b

991

### Norbeck, J., Latimer, T., Gradl, C., Agarwal, S., Dadi, S., Eddy, E., Fercho, S., Lang, C.,

992

### McConville, E., Titov, A. and Voller, K., (2023). A review of drilling, completion, and

993

### stimulation of a horizontal geothermal well system in North-Central Nevada. In _Proceedings of_

994

### _the 48th Workshop on Geothermal Reservoir Engineering_ (pp. 6-8). Stanford University

995

### California, USA.

996

### Ricks, W., Norbeck, J., & Jenkins, J. D. (2022). The value of in-reservoir energy storage for

997

### flexible dispatch of geothermal power. Applied Energy, 313, 118807.

998

### https://doi.org/10.1016/j.apenergy.2022.118807

999

### Ricks, W., Voller, K., Galban, G., Norbeck, J., & Jenkins, J. D. (2024). The role of flexible

1000

### geothermal power in decarbonized electricity systems. Nature Energy.

1001

https://doi.org/10.1038/s41560-023-01437-y 1002

### Rodríguez-Pradilla, G., Eaton, D.W., & Verdon, J.P. (2022). Basin-scale multi-decadal analysis

1003

### of hydraulic fracturing and seismicity in western Canada shows non-recurrence of induced

1004

### runaway fault rupture. Scientific Reports, 12(1), 1–14. https://doi.org/10.1038/s41598-022-

1005

### 18505-0

1006

manuscript submitted to _JGR: Solid Earth_

### Ruhl, C. J., R. E. Abercrombie, K. D. Smith, and I. Zaliapin (2016), Complex spatiotemporal

1007

### evolution of the 2008 Mw 4.9 Mogul earthquake swarm (Reno, Nevada): Interplay of fluid and

1008

### faulting, J. Geophys. Res. Solid Earth, 121, 8196–8216, doi:10.1002/2016JB013399

1009

### Rutledge, J., & Phillips, W. S. (2003). Hydraulic stimulation of natural fractures as revealed by

1010

### induced microearthquakes, Carthage Cotton Valley gas field, east Texas. Geophysics, 68(2),

1011

### 441–452. https://doi.org/10.1190/1.1567214

1012

### Scholz, C. H. (2015). On the stress dependence of the earthquake b value. Geophysical Research

1013

### Letters, 42(5), 1399–1402. https://doi.org/10.1002/2014gl062863

1014

### Sepulveda, N. A., Jenkins, J. D., De Sisternes, F. J., & Lester, R. K. (2018). The role of Firm

1015

### Low-Carbon Electricity Resources in deep decarbonization of power generation. Joule, 2(11),

1016

2403–2420. https://doi.org/10.1016/j.joule.2018.08.006 1017

### Shapiro, S. A., Dinske, C., Langenbruch, C., & Wenzel, F. (2010). Seismogenic index and

1018

### magnitude probability of earthquakes induced during reservoir fluid stimulations. The Leading

1019

### Edge, 29(3), 304-309.

1020

### Shapiro, S. A., O. S. Krüger, C. Dinske, and C. Langenbruch (2011), Magnitudes of induced

1021

### earthquakes and geometric scales of fluid-stimulated rock volumes, Geophysics, 76(6), WC55–

1022

### WC63, doi:10.1190/geo2010-0349.1.

1023

### Shapiro, S. A. (2015). Fluid-induced seismicity. Cambridge University Press.

1024

### https://doi.org/10.1017/cbo9781139051132

1025

### Shapiro, S. A., Dinske, C., & Rothert, E. (2006). Hydraulic‐fracturing controlled dynamics of

1026

### microseismic clouds. Geophysical Research Letters, 33(14).

1027

### https://doi.org/10.1029/2006gl026365

1028

manuscript submitted to _JGR: Solid Earth_

### Shapiro, S. A., Huenges, E., & Borm, G. (1997). Estimating the crust permeability from fluid-

1029

### injection-induced seismic emission at the KTB site. Geophysical Journal International, 131(2),

1030

### F15–F18. https://doi.org/10.1111/j.1365-246x.1997.tb01215.x

1031

### Shapiro, S. A., Rothert, E., Rath, V., & Rindschwentner, J. (2002). Characterization of fluid

1032

### transport properties of reservoirs using induced microseismicity. Geophysics, 67(1), 212–220.

1033

### https://doi.org/10.1190/1.1451597

1034

### Shi, Y., & Bolt, B. A. (1982). The standard error of the magnitude-frequency b value. Bulletin of

1035

### the Seismological Society of America, 72(5), 1677–1687.

1036

### https://doi.org/10.1785/bssa0720051677

1037

### Schultz, R., Beroza, G. C., & Ellsworth, W. L. (2021). A risk-based approach for managing

1038

### hydraulic fracturing–induced seismicity. Science, 372(6541), 504–507.

1039

### https://doi.org/10.1126/science.abe2174

1040

### Spica, Z., Ajo‐Franklin, J., Beroza, G. C., Biondi, B., Cheng, F., Gaite, B., et al. (2023).

1041

### PUBDAS: a PUBLIC distributed acoustic sensing datasets repository for geosciences.

1042

### Seismological Research Letters, 94(2A), 983–998. https://doi.org/10.1785/0220220279

1043

### Templeton, D.C., Matzel, E.M., & Trenton, T.C. (2017). Evolution of Microseismicity at the

1044

### Blue Mountain Geothermal Site, GRC Transactions, 41, 1752-1755.

1045

### Trugman, D. (2024). A High‐Precision Earthquake Catalog for Nevada. Seismological Research

1046

### Letters 2024; doi: https://doi.org/10.1785/0220240106

1047

### Titov, A., Dadi, S., Galban, G., Norbeck, J., M. Almasoodi, Pelton, K., Bowie, C., J. Haffener, &

1048

### K. Haustveit. (2024). Optimization of Enhanced Geothermal System Operations Using

1049

### Distributed Fiber Optic Sensing and Offset Pressure Monitoring. Paper presented at the SPE

1050

manuscript submitted to _JGR: Solid Earth_

### Hydraulic Fracturing Technology Conference and Exhibition, The Woodlands, Texas, USA.

1051

### https://doi.org/10.2118/217810-MS

1052

### van der Elst, N. J., Page, M. T., Weiser, D. A., Goebel, T. H., & Hosseini, S. M. (2016). Induced

1053

### earthquake magnitudes are as large as (statistically) expected. Journal of Geophysical Research:

1054

### Solid Earth, 121(6), 4575–4590. https://doi.org/10.1002/2016jb012818

1055

### Verdon, J. P., & Budge, J. (2018). Examining the Capability of Statistical Models to Mitigate

1056

### Induced Seismicity during Hydraulic Fracturing of Shale Gas Reservoirs. Bulletin of the

1057

### Seismological Society of America, 108(2), 690–701. https://doi.org/10.1785/0120170207

1058

### Verdon, J. P., Horne, S., Clarke, A., Stork, A., Baird, A. F., & Kendall, J. (2020). Microseismic

1059

### monitoring using a fibre-optic Distributed Acoustic Sensor (DAS) array. Geophysics, 1–48.

1060

### https://doi.org/10.1190/geo2019-0752.1

1061

### Wiemer, S., & Wyss, M. (2000). Minimum Magnitude of Completeness in Earthquake Catalogs:

1062

### Examples from Alaska, the Western United States, and Japan, the western United States, and

1063

### Japan. Bulletin of the Seismological Society of America, 90(4), 859–869.

1064

### https://doi.org/10.1785/0119990114

1065

### Woessner, J., & Wiemer, S. (2005). Assessing the quality of earthquake catalogues: Estimating

1066

### the magnitude of completeness and its uncertainty. Bulletin of the Seismological Society of

1067

### America, 95(2), 684–698. https://doi.org/10.1785/0120040007

1068

### Yin, J., Soto, M. A., Ramírez, J., Kamalov, V., Zhu, W., Husker, A., & Zhan, Z. (2023a). Real-

1069

### Data testing of distributed acoustic sensing for offshore earthquake early warning. The Seismic

1070

### Record, 3(4), 269–277. https://doi.org/10.1785/0320230018

1071

manuscript submitted to _JGR: Solid Earth_

### Yin, J., Zhu, W., Li, J., Biondi, E., Miao, Y., Spica, Z. J., et al. (2023b). Earthquake magnitude

1072

### with DAS: A transferable data-based scaling relation. Geophysical Research Letters, 50,

1073

### e2023GL103045. https://doi.org/10.1029/2023GL103045

1074

### Zeng, X., Zhang, H., Zhang, X., Wang, H., Zhang, Y., & Liu, Q. (2014). Surface microseismic

1075

### monitoring of hydraulic fracturing of a shale‐gas reservoir using short‐period and broadband

1076

### seismic sensors. Seismological Research Letters, 85(3), 668-677

1077

### Zhebel, V. M., & Eisner, L. (2015). Simultaneous microseismic event localization and source

1078

### mechanism determination. Geophysics, 80(1), KS1–KS9. https://doi.org/10.1190/geo2014-

1079

### 0055\.1

1080

### Zhu, W., Allison, K.L., Dunham, E.M., & Yang, Y. (2020). Fault valving and pore pressure

1081

### evolution in simulations of earthquake sequences and aseismic slip. Nature Communications,

1082

### 11(1), 1–11. https://doi.org/10.1038/s41467-020-18598-z

1083

### Zinno, R. J., Gibson, J. B., Walker, R. N., & Withers, R. J. (1998). Overview: Cotton Valley

1084

### hydraulic fracture imaging project. SEG Annual Meeting Expanded Abstracts 17, 338–341.

1085

### https://doi.org/10.1190/1.1820642

1086

1087