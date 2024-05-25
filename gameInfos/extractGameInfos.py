import json
import os

BASE_PATH = os.path.expandvars("%LOCALAPPDATA%low\\tobspr Games\\shapez 2\\")
BUILDINGS_PATH = BASE_PATH + "buildings-metadata.json"
ADDITIONAL_BUILDINGS_PATH = "./gameInfos/additionalBuildings.json"
RESEARCH_PATH = BASE_PATH + "research-metadata-full.json"
EXTRACTED_BUILDINGS_PATH = "./gameInfos/buildings.json"
EXTRACTED_RESEARCH_PATH = "./gameInfos/research.json"
EXTRACTED_ISLANDS_PATH = "./gameInfos/islands.json"

def extractKeys(fromDict:dict,toDict:dict,keys:list[str]) -> dict:
    for key in keys:
        toDict[key] = fromDict[key]
    return toDict



def main() -> None:

    if os.getcwd().split("\\")[-1] != "fake shape bot":
        print("Must be executed from 'fake shape bot' directory")
        input()
        exit()

    # research
    # with open(RESEARCH_PATH,encoding="utf-8") as f:
    #     researchRaw = json.load(f)

    # gameVersion = researchRaw["GameVersion"]
    # extractedResearch = {"GameVersion":gameVersion}
    # extractedLevels = []
    # keys = ["Id","Title","Description","GoalShape","GoalAmount","Unlocks"]
    # for levelRaw in researchRaw["Levels"][1:]:
    #     extractedLevels.append({
    #         "Node" : extractKeys(levelRaw["Node"],{},keys),
    #         "SideGoals" : [extractKeys(sg,{},keys) for sg in levelRaw["SideGoals"]]
    #     })
    # extractedResearch["Levels"] = extractedLevels

    # with open(EXTRACTED_RESEARCH_PATH,"w",encoding="utf-8") as f:
    #     json.dump(extractedResearch,f,indent=4,ensure_ascii=True)
    gameVersion = "0.0.0-alpha20"



    # buildings

    with open(BUILDINGS_PATH,encoding="utf-8") as f:
        buildingsRaw = json.load(f)
    with open(ADDITIONAL_BUILDINGS_PATH,encoding="utf-8") as f:
        additionalBuildings = json.load(f)

    toRemoveBuildings = []
    for ab in additionalBuildings:
        if ab["Id"] in (b["Id"] for b in buildingsRaw):
            toRemoveBuildings.append(ab["Id"])
        else:
            print(f"Additonal building {ab['Id']} not in base buildings")

    buildingsRaw = [b for b in buildingsRaw if b["Id"] not in toRemoveBuildings]
    extractedBuildings:dict[str,str|list] = {"GameVersion":gameVersion,"Buildings":[]}
    for variantListRaw in additionalBuildings+buildingsRaw:
        curVariantListKeys = ["Id"]
        if variantListRaw.get("Title") is not None:
            curVariantListKeys.append("Title")
        extractedVariantList = extractKeys(variantListRaw,{},curVariantListKeys)
        extractedVariantList["Variants"] = []
        for internalVariantListRaw in variantListRaw["Variants"]:
            curInternalVariantListKeys = ["Id"]
            if internalVariantListRaw.get("Title") is not None:
                curInternalVariantListKeys.append("Title")
            extractedInternalVariantList = extractKeys(internalVariantListRaw,{},curInternalVariantListKeys)
            extractedInternalVariantList["InternalVariants"] = []
            for buildingRaw in internalVariantListRaw["InternalVariants"]:
                extractedBuilding = extractKeys(buildingRaw,{},["Id","Tiles"])
                extractedInternalVariantList["InternalVariants"].append(extractedBuilding)
            extractedVariantList["Variants"].append(extractedInternalVariantList)
        extractedBuildings["Buildings"].append(extractedVariantList)

    with open(EXTRACTED_BUILDINGS_PATH,"w",encoding="utf-8") as f:
        json.dump(extractedBuildings,f,indent=4,ensure_ascii=True)



    # islands
    with open(EXTRACTED_ISLANDS_PATH,encoding="utf-8") as f:
        islandsRaw = json.load(f)
    islandsRaw["GameVersion"] = gameVersion
    print("Check if islands have changed and remember to use /blueprint-creator all-buildings and all-islands")
    with open(EXTRACTED_ISLANDS_PATH,"w",encoding="utf-8") as f:
        json.dump(islandsRaw,f,indent=4,ensure_ascii=True)



if __name__ == "__main__":
    main()