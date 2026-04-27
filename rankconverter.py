# ns = new system (apr 2026)
# os = old system (before the addition of the champion tiers)

nsDivWidth = 100 # 100 SR per division
# (4000/40 assuming bronze 5 is 1000sr in both systems, 
# giving 1000-5000 as the full skill range, 
# though this technically was not the case in overwatch 1)
osDivWidth = 4000/35 # 35 divisions excluding the champion rank

rankPrefix = ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grandmaster", "Champion"]

def osDivToRank(osDiv):
    if osDiv <= 0:
        return {"tier": "Bronze", "div": 5, "percent": 0}
    if osDiv >= 35:
        return {"tier": "Grandmaster", "div": 1, "percent": 100}
    
    tier = int(osDiv // 5)
    divInTier = osDiv % 5

    divNum = 5 - int(divInTier)
    percent = round((divInTier - int(divInTier)) * 100)
    return {"tier": rankPrefix[tier], "div": divNum, "percent": percent}

def convertRank(nsRank):
    osDiv = (nsRank - 1000) / osDivWidth
    return osDiv

if __name__ == "__main__":
    nsRank = int(input())
    osDiv = convertRank(nsRank)
    rank = osDivToRank(osDiv)
    print(osDiv)
    print(f"{rank['tier']} {rank['div']} {rank['percent']}%")