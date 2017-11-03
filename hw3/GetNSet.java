import java.util.concurrent.atomic.AtomicIntegerArray;

class GetNSet implements State {
    private AtomicIntegerArray value;
    private byte maxval;

	private void createAtomicArray(byte[] v){
    	int[] intArray = new int[v.length];
    	for(int i = 0; i < v.length; i++){
    		intArray[i] = v[i];
		}
		value = new AtomicIntegerArray(intArray);
	}

    GetNSet(byte[] v) { 
    	maxval = 127;
    	createAtomicArray(v);
    }

    GetNSet(byte[] v, byte m) { 
    	maxval = m;
    	createAtomicArray(v);
    }
    public int size() { return value.length();}
    public byte[] current() { 
		byte[] ret = new byte[value.length()];
		for(int i = 0; i < ret.length; i++){
			ret[i] = (byte) value.get(i);
		}
		return ret;
	}
	public boolean swap(int i, int j) {
		if (value.get(i) <= 0 || value.get(j) >= maxval) {
			return false;
		}
		value.getAndDecrement(i);
		value.getAndIncrement(j);
		return true;
	}
}
