kitty_zoo <- read.csv("MayaDeerMetrics_Cantryll_Emeryedits.csv", header = TRUE)
kitty_mod <- read.csv("EAP Florida Modern Deer Measurements_FORFUTRES_1_23_2020.csv", header = TRUE)
aepyceros <- read.csv("Extant Aepyceros database_updated 11_2016.csv", header = TRUE)
or_cougars <- read.csv("1987-2019 Cougar Weight-Length Public Request.csv", header = TRUE)
ray_horse <- read.csv("00_ExtantEquus_9_22_2019.csv", header = TRUE)
helena_horse <- read.csv("Horse data_Helena.csv", header = TRUE)
spermophilus <- read.csv("biogeo.csv", header = TRUE)
vert_deer <- read.csv("ODOVIRGCLEAN.csv", header = TRUE)

hist(log10(kitty_mod$Total.Fresh.Weight..g.))
hist(aepyceros$Weight)
hist(or_cougars$Weight) #in lbs
hist(spermophilus$body.mass.g)
hist(log10(vert_deer$X1st_body_mass))

plot(kitty_mod$Weight.of.viscera..g. ~ kitty_mod$Total.Fresh.Weight..g.)
plot(kitty_mod$Total.bone.weight..g. ~ kitty_mod$Total.Fresh.Weight..g.)
plot(kitty_mod$Skin.weight..g. ~ kitty_mod$Total.Fresh.Weight..g.)

