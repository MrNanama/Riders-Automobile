debug = True
ASGARI_YUKSEKLIK = 80.0
AZAMI_YUKSEKLIK = 100.0
sensitivity = 0.02

import math


class Cezeri(CezeriParent):

    def __init__(self, id=0):
        super().__init__(id=id, keyboard=False, sensor_mode=DUZELTILMIS)
        self.baslangic_bolgesi = self.harita.bolge(self.gnss.enlem, self.gnss.boylam)
        self.ilk = False
        self.iki = False
        self.irtifa_saglandi = False
        self.treshold = 15
        self.boylam_saglandi = False
        self.enlem_saglandi = False
        self.phase = 0

        self.onde_engel_var_asmaya_calisiyorum = False

        print(self.harita.bolge(-319, -421).enlem, self.harita.bolge(-321, -419).boylam)
        print(self.hedefler[0].bolge.enlem, self.hedefler[0].bolge.boylam)

    def norm(self, aci):
        return (aci + 20 * math.pi) % (2 * math.pi)

    def hangi_yon_on(self, aci):
        aci = self.norm(aci)

        hangi_yon = 1
        min_fark = min(self.norm(aci - 0), self.norm(0 - aci))

        if min(self.norm(aci - math.pi), self.norm(math.pi - aci)) < min_fark:
            hangi_yon = 7
            min_fark = min(self.norm(aci - math.pi), self.norm(math.pi - aci))
        if min(self.norm(aci - math.pi / 2), self.norm(math.pi - aci / 2)) < min_fark:
            hangi_yon = 3
            min_fark = min(self.norm(aci - math.pi / 2), self.norm(math.pi - aci / 2))
        if min(self.norm(aci + math.pi / 2), self.norm(-math.pi / 2 - aci)) < min_fark:
            hangi_yon = 5
            min_fark = min(self.norm(aci + math.pi / 2), self.norm(-math.pi / 2 - aci))

        return hangi_yon

    def onumuz_engel_mi(self):
        konum = self.gnss

        if self.hangi_yon_on(self.manyetometre.veri) == 1:
            hedef_bolge = self.harita.bolge(konum.enlem + 20, konum.boylam)
        elif self.hangi_yon_on(self.manyetometre.veri) == 7:
            hedef_bolge = self.harita.bolge(konum.enlem - 20, konum.boylam)
        elif self.hangi_yon_on(self.manyetometre.veri) == 3:
            hedef_bolge = self.harita.bolge(konum.enlem, konum.boylam - 20)
        elif self.hangi_yon_on(self.manyetometre.veri) == 5:
            hedef_bolge = self.harita.bolge(konum.enlem, konum.boylam + 20)

        return hedef_bolge.ruzgar or (hedef_bolge.yukselti >= self.gnss.irtifa)

    def sagimiz_engel_mi(self):
        konum = self.gnss

        if self.hangi_yon_on(self.manyetometre.veri) == 1:
            hedef_bolge = self.harita.bolge(konum.enlem, konum.boylam + 20)
        elif self.hangi_yon_on(self.manyetometre.veri) == 7:
            hedef_bolge = self.harita.bolge(konum.enlem, konum.boylam - 20)
        elif self.hangi_yon_on(self.manyetometre.veri) == 3:
            hedef_bolge = self.harita.bolge(konum.enlem + 20, konum.boylam)
        elif self.hangi_yon_on(self.manyetometre.veri) == 5:
            hedef_bolge = self.harita.bolge(konum.enlem - 20, konum.boylam)

        return hedef_bolge.ruzgar or (hedef_bolge.yukselti >= self.gnss.irtifa)

    def solumuz_engel_mi(self):
        konum = self.gnss

        if self.hangi_yon_on(self.manyetometre.veri) == 1:
            hedef_bolge = self.harita.bolge(konum.enlem, konum.boylam - 20)
        elif self.hangi_yon_on(self.manyetometre.veri) == 7:
            hedef_bolge = self.harita.bolge(konum.enlem, konum.boylam + 20)
        elif self.hangi_yon_on(self.manyetometre.veri) == 3:
            hedef_bolge = self.harita.bolge(konum.enlem - 20, konum.boylam)
        elif self.hangi_yon_on(self.manyetometre.veri) == 5:
            hedef_bolge = self.harita.bolge(konum.enlem + 20, konum.boylam)

        return hedef_bolge.ruzgar or (hedef_bolge.yukselti >= self.gnss.irtifa)

    def sol_on_engel_mi(self):
        konum = self.gnss

        if self.hangi_yon_on(self.manyetometre.veri) == 1:
            hedef_bolge = self.harita.bolge(konum.enlem + 20, konum.boylam - 20)
        elif self.hangi_yon_on(self.manyetometre.veri) == 7:
            hedef_bolge = self.harita.bolge(konum.enlem - 20, konum.boylam + 20)
        elif self.hangi_yon_on(self.manyetometre.veri) == 3:
            hedef_bolge = self.harita.bolge(konum.enlem - 20, konum.boylam - 20)
        elif self.hangi_yon_on(self.manyetometre.veri) == 5:
            hedef_bolge = self.harita.bolge(konum.enlem + 20, konum.boylam + 20)

        return hedef_bolge.ruzgar or (hedef_bolge.yukselti >= self.gnss.irtifa)

    def irtifa_sagla(self):
        if self.gnss.irtifa >= AZAMI_YUKSEKLIK:
            # debug and print("-----IRTIFA ASAGI-----")
            self.asagi_git(HIZLI)
        elif self.gnss.irtifa <= ASGARI_YUKSEKLIK:
            # debug and print("-----IRTIFA YUKARI-----")
            self.yukari_git(HIZLI)
        else:
            # print("DUR")
            self.dur()
            self.phase = 1

    def enlem_sagla(self, destinasyon):
        if abs(self.gnss.enlem - destinasyon.bolge.enlem) > self.treshold:
            if self.gnss.enlem - destinasyon.bolge.enlem > 0:
                if self.onumuz_engel_mi():
                    if self.boylam_saglandi and self.onde_engel_var_asmaya_calisiyorum == False:
                        self.dur()
                        self.onde_engel_var_asmaya_calisiyorum = True
                        self.boylam_saglandi = False

                    if self.onde_engel_var_asmaya_calisiyorum:
                        self.saga_git(ORTA)
                    return False
                else:
                    if self.sol_on_engel_mi() == False and self.onde_engel_var_asmaya_calisiyorum == True:
                        self.onde_engel_var_asmaya_calisiyorum = False
                        self.dur()

                self.ileri_git(HIZLI)
            else:
                self.geri_git(HIZLI)
        else:
            self.dur()
            self.enlem_saglandi = True
            self.treshold /= 2

    def boylam_sagla(self, destinasyon):
        if abs(self.gnss.boylam - destinasyon.bolge.boylam) > self.treshold:
            if self.gnss.boylam - destinasyon.bolge.boylam > 0:
                if self.sagimiz_engel_mi():
                    if abs(self.imu.hiz.z) > 0.2:
                        self.dur()
                    return False

                self.saga_git(HIZLI)
            else:
                if self.solumuz_engel_mi():
                    if abs(self.imu.hiz.z) > 0.2:
                        self.dur()
                    return False

                self.sola_git(HIZLI)
        else:
            self.dur()
            self.boylam_saglandi = True

    def aciya_don(self, hedef_aci):

        aci = (self.manyetometre.veri + 2 * math.pi) % (2 * math.pi)
        hedef_aci = (hedef_aci + 2 * math.pi) % (2 * math.pi)

        if (hedef_aci - aci + 6 * math.pi) % (2 * math.pi) <= math.pi:
            self.don(min(2 * abs(hedef_aci - aci), 4))
        else:
            self.don(max(-2 * abs(aci - hedef_aci), -4))

        aci = (self.manyetometre.veri + 2 * math.pi) % (2 * math.pi)

        if abs(hedef_aci - aci) < sensitivity:
            self.don(0)

    def hedefegit(self, hedef, treshold, phase):

        # if hedef.bolge.enlem - self.gnss.enlem < 0:
        # eğer aynı enlemdeyse dönmeyecek mi
        self.aciya_don(3.14)

        if not self.enlem_saglandi:
            self.enlem_sagla(hedef)

        if (not self.boylam_saglandi) and (not self.onde_engel_var_asmaya_calisiyorum):
            self.boylam_sagla(hedef)

        if self.enlem_saglandi and self.boylam_saglandi:
            print("SAĞLANDI")
            self.enlem_saglandi = False
            self.boylam_saglandi = False
            self.phase = phase
            self.treshold = treshold

    def run(self):
        print(self.onumuz_engel_mi(), self.sol_on_engel_mi(), self.solumuz_engel_mi(),
              self.onde_engel_var_asmaya_calisiyorum)

        if self.phase == 0:
            self.irtifa_sagla()
        elif self.phase == 1:
            self.hedefegit(self.hedefler[0], 1, 2)

        elif self.phase == 2:
            self.hedefegit(self.hedefler[0], 1, 3)

        elif self.phase == 3:
            print("phase 3")
            self.asagi_git(ORTA)

        # print(self.gnss)


cezeri_1 = Cezeri(id=1)
cezeri_2 = Cezeri(id=2)

while robot.is_ok():
    if cezeri_1.iki:
        cezeri_1.dur()
    else:
        cezeri_1.run()