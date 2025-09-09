import sys
# 패키지 설치 경로 추가
# pip install --target=D:\seolgit\python_packages numpy matplotlib
# 위 명령으로 지정 폴더에 패키지 설치 후, sys.path.append로 경로를 파이썬에 알려줌
sys.path.append(r"D:\seolgit\python_packages")  # 패키지가 설치된 경로 지정

# 사용할 외부 패키지(설치함)
import numpy as np                  # 수치 계산 (배열, 지수함수 등)
import matplotlib.pyplot as plt     # 그래프 그리기

# -------------------------------
# 사용되는 기본 물리 상수 (SI 단위계)
# -------------------------------
h = 6.62607015e-34      # 플랑크 상수 [J·s]
c = 2.99792458e8        # 빛의 속도 [m/s]
k = 1.380649e-23        # 볼츠만 상수 [J/K]

# -------------------------------
# 플랑크의 복사 법칙 (에너지 밀도 표현)
# lam : 파장 [m]
# T   : 절대온도 [K]
# 반환값 : u_lambda [J·m^-4] (J/m^3 per m)
# -------------------------------
def u_lambda(lam, T):
    a = 8 * np.pi * h * c / (lam**5)
    b = h * c / (lam * k * T)
    return a / (np.exp(b) - 1)

# -------------------------------
# 계산할 파장 범위 설정
# -------------------------------
w_nm = np.linspace(0, 3000, 1000)   # 파장 (nm 단위)
lam = w_nm * 1e-9                   # m 단위 변환

# -------------------------------
# 여러 온도에서 흑체복사 곡선 (절대값) 그리기
# -------------------------------
temps = [2500, 3000, 3500, 4000, 4500, 5000, 5500]     # K
fig, ax = plt.subplots()             # figure + axes 객체 생성(원점이 떠보이는 것 방지)
for T in temps:
    u = u_lambda(lam, T)             # [J m^-4]
    u_kJ_per_nm = u * 1e-12          # J→kJ(×1e-3), per m→per nm(×1e-9) ⇒ ×1e-12
    ax.plot(w_nm, u_kJ_per_nm, label=f"{T} K")

# -------------------------------
# Wien 꼭짓점(피크) 점 + 점선
# λ_max = b/T,  b ≈ 2.897771955×10^-3 m·K  (= 2.897771955×10^6 nm·K)
# -------------------------------
b_wien_mK  = 2.897771955e-3          # m·K
peak_x_nm  = []
peak_y_kjn = []
for T in temps:
    lam_max = b_wien_mK / T          # [m]
    x_nm    = lam_max * 1e9          # [nm]
    y_kjn   = u_lambda(lam_max, T) * 1e-12  # [kJ/nm]
    peak_x_nm.append(x_nm)
    peak_y_kjn.append(y_kjn)
    ax.plot(x_nm, y_kjn, "o", color="k", markersize=4)  # 꼭짓점 표시

ax.plot(peak_x_nm, peak_y_kjn, "k--", linewidth=1, label="Wien's law")

# -------------------------------
# 가시광선 범위 수직선 (380 nm, 750 nm)
# -------------------------------
ax.axvline(380, color="gray", linestyle=":", linewidth=1, label="Visible range")
ax.axvline(750, color="gray", linestyle=":", linewidth=1)

# -------------------------------
# 라벨/제목/범례
# -------------------------------
ax.set_xlabel("Wavelength (nm)")
ax.set_ylabel(r"$u(\lambda)$ ($10^{-7}$ kJ/nm)")  # 지수 포함 라벨(숫자는 그대로)
ax.set_title("Blackbody radiation")
ax.legend(title="Temperature", loc="upper right")

# 원점이 꼭짓점에 붙도록 설정
ax.set_xlim(0, 3000)    # x축 0~3000 nm
ax.set_ylim(0, None)    # y축 0부터 시작
ax.margins(x=0, y=0)    # x, y축 여백 제거
ax.yaxis.get_offset_text().set_visible(False)  # 축 위쪽 1e-? 표시 제거

plt.tight_layout()

# -------------------------------
# 결과 저장 (벡터)
# -------------------------------
plt.savefig("blackbody_u_lambda.svg")
plt.savefig("blackbody_u_lambda.pdf")

# -------------------------------
# 화면 출력
# -------------------------------
plt.show()