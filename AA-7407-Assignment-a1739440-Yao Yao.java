public class Stone {

    static int[] silver = {11,9,13,10};
    static int[] gold = {8,14,17,21};
    static float totalLeft = 0;
    public static void main(String[] args){

        float[] xProp = new float[silver.length];
        float[] initialSolution = initial(silver, gold);
        float[] currentBest = initialSolution;
        int i = 0;
        float currentMoney = getMoney(currentBest);
        System.out.println("initial money : " + currentMoney);
        float newMoney;
        while ( i < 100){
            float[] newSolution = mutation(currentBest);
            newMoney = getMoney(newSolution);
            if (newMoney > currentMoney){
                currentBest = newSolution;
                currentMoney = newMoney;
                System.out.println("New Best Money: " + currentMoney);
            }
            System.out.println("No. " + i);
            i++;
        }
        System.out.println(" Best Money: " + currentMoney);

    }

    public static float getMoney(float[] solution){
        float currentMoney = 0;
        for(int i = 0; i < solution.length; i++){
            currentMoney += silver[i]*solution[i];
            //System.out.println("current silver: "+ i +" " + silver[i]);
        }
        return currentMoney;
    }

    public static float[] mutation(float[] currentBest){
        float[] newSolution = currentBest;

        for(int m = 0; m < currentBest.length ; m++){
            if (newSolution[m] > 0 && newSolution[m] < 1){
                newSolution[m] = 0;
                break;
            }
        }
/*
        for(int m = 0 ; m < newSolution.length ; m++){
            System.out.print(newSolution[m]+ " ,,, ");
        }
        */
        while (satisfiable(newSolution)) {
            newSolution = addNewElement(newSolution);
        }


        while (satisfiable2(newSolution)) {
            newSolution = cutElement(newSolution);
        }

        return newSolution;
    }

    public static float[] addNewElement(float[] newSolution){
        int randomPick = 0;
        do {
            //System.out.println("newSolution[randomPick]: "+newSolution[randomPick]);
            randomPick = (int)(Math.random()*newSolution.length);
            //System.out.println(" randomPick1:" + randomPick);
        } while (newSolution[randomPick] != 0);
        newSolution[randomPick] = 1;
        return newSolution;
    }

    public static float[] cutElement(float[] newSolution) {
        int randomPick = 0;
        float currentTaken = 0;
        float[] insteadSolution = new float[newSolution.length];
        do {
            currentTaken = 0;
            for (int i = 0; i < newSolution.length; i++){
                insteadSolution[i] = newSolution[i];
            }
            do {
                //System.out.println("newSolution[randomPick]: "+newSolution[randomPick] + "  totalLeft: " + totalLeft);
                randomPick = (int) (Math.random() * newSolution.length);
                //System.out.println(" randomPick2:" + randomPick);
            } while (newSolution[randomPick] == 0);
            //System.out.println("di");
            for (int n = 0; n < newSolution.length; n++) {
                currentTaken += newSolution[n] * (gold[n] + silver[n]);
            }
            insteadSolution[randomPick] = (totalLeft - (currentTaken - (gold[randomPick] + silver[randomPick]))) / (gold[randomPick] + silver[randomPick]);
            /*
            for (int i = 0; i < newSolution.length; i++){
                System.out.println("insteadSolution[]"+ i + "  " + insteadSolution[i] + "    " + newSolution[i]);
            }
            */
        }while(insteadSolution[randomPick]<=0 || insteadSolution[randomPick]>=1);
        //System.out.println("da");
        return insteadSolution;
    }

    public static boolean satisfiable(float[] newSolution){
        float currentTotal = 0;
        for(int m = 0; m < newSolution.length; m++){
            currentTotal += newSolution[m] * (silver[m] + gold[m]);
        }
        if(currentTotal >= totalLeft){
            //System.out.println("Larger ： "+totalLeft);
            return false;
        }else {
            return true;
        }
    }

    public static boolean satisfiable2(float[] newSolution){
        float currentTotal = 0;
        for(int m = 0; m < newSolution.length; m++){
            currentTotal += newSolution[m] * (silver[m] + gold[m]);
            //System.out.println("silver[m] + gold[m] " + newSolution[m] + " " + silver[m] + " " + gold[m]);
        }
        if(currentTotal == totalLeft){
            return false;
        }else {
            //System.out.println("currentTotal: " + currentTotal);
            return true;
        }
    }

    public static float[] initial(int[] silver, int[] gold){

        int[] silverOrder = new int[silver.length];
        int[] goldOrder = new int[silver.length];
        float left = 0;
        float[] initialSolution = new float[silver.length];
        int[] indicate = new int[silver.length];
        for(int i = 0 ; i < indicate.length ; i++){
            silverOrder[i] = silver[i];
            goldOrder[i] = gold[i];
            indicate[i] = i;
            left += gold[i];
        }
        totalLeft = left;
        int change = 0;
        for(int i = 0 ; i < silver.length - 1; i++){
            for(int j = 0; j < silver.length - (i+1); j++){
                if(silverOrder[j] < silverOrder[j+1]){

                    change = silverOrder[j];
                    silverOrder[j] = silverOrder[j+1];
                    silverOrder[j+1] = change;

                    change = goldOrder[j];
                    goldOrder[j] = goldOrder[j+1];
                    goldOrder[j+1] = change;

                    change = indicate[j];
                    indicate[j] = indicate[j+1];
                    indicate[j+1] = change;
                }
            }
        }
        for(int i = 0 ; i < indicate.length ; i++){
            //System.out.println(silver[]);
        }
        int i = 0;
        while(left!=0){
            left = left - goldOrder[i] - silverOrder[i];
            if (left < 0){
                initialSolution[indicate[i]] = (silverOrder[i] + goldOrder[i] + left) / (silverOrder[i] + goldOrder[i]);
                break;
            }else {
                initialSolution[indicate[i]] = 1;
                //System.out.println("indicate "+i+ " : " + indicate[i]);
            }
            i++;
        }
        System.out.print("initialSolution : ");
        for(int m = 0 ; m < initialSolution.length ; m++){
            System.out.print(initialSolution[m]+ " , ");
        }
        return initialSolution;
    }

}
