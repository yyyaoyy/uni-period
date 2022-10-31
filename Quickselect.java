import java.util.Random;
public class Quickselect {
    public int findKthSmallest(int[] nums, int k) {
        if (nums == null || nums.length == 0) {
            return Integer.MIN_VALUE;
        }
        int len = nums.length;
        return quickSelect(nums, k, 0, len - 1);
    }

    private int quickSelect(int[] nums, int k, int start, int end) {

        //Choose a pivot randomly
        Random rand = new Random();
        int index = rand.nextInt(end - start + 1) + start;
        int pivot = nums[index];
        swap(nums, index, end);

        int left = start, right = end;

        while(left < right) {
            if (nums[left++] >= pivot) {
                swap(nums, --left, --right);
            }
        }
        //left is now pointing to the first number that is greater than or equal to the pivot
        swap(nums, left, end);
        //m is the number of numbers that is smaller than pivot
        int m = left - start;

        if (m == k - 1) { //in order to find the kth smallest number, there must be k - 1 number smaller than it
            return pivot;
        }
        else if (k <= m) { //target is in the left subarray
            return quickSelect(nums, k, start, left - 1);
        }
        else {
            //target is in the right subarray, but need to update k
            //Since we have discarded m numbers smaller than it which is in the right subarray
            return quickSelect(nums, k - m, left, end);
        }
    }

    private void swap(int[] nums, int o, int l) {
        int tmp = nums[o];
        nums[o] = nums[l];
        nums[l] = tmp;
    }
   public static void main(String[] args) {
       Quickselect m = new Quickselect();
 /*      System.out.println(m.quickSelect(new int []{96, 47, 95, 38, 53, 45, 3, 92, 20, 73},1,0,9));
       System.out.println(m.quickSelect(new int []{96, 47, 95, 38, 53, 45, 3, 92, 20, 73},2,0,9));
       System.out.println(m.quickSelect(new int []{96, 47, 95, 38, 53, 45, 3, 92, 20, 73},3,0,9));
       System.out.println(m.quickSelect(new int []{96, 47, 95, 38, 53, 45, 3, 92, 20, 73},6,0,9));
 */    //  System.out.println(m.quickSelect(new int []{4, 2, 1, 7, 5, 3, 8, 10, 9, 6},2,0,9));
       System.out.println(m.quickSelect(new int []{62, 66, 70, 54, 74, 98, 83, 52, 80, 19},1,0,9));
       System.out.println(m.quickSelect(new int []{62, 66, 70, 54, 74, 98, 83, 52, 80, 19},2,0,9));
       System.out.println(m.quickSelect(new int []{62, 66, 70, 54, 74, 98, 83, 52, 80, 19},3,0,9));
       System.out.println(m.quickSelect(new int []{62, 66, 70, 54, 74, 98, 83, 52, 80, 19},6,0,9));
    }
}