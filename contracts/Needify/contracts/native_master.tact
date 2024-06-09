import "@stdlib/deploy";
import "./native_wallet";
import "@stdlib/ownable";

struct MasterData {
    total_supply: Int;
    mintable: Bool;
    owner: Address;
    jetton_content: Cell;
    jetton_wallet_code: Cell;
}

@interface("org.ton.jetton.master")
contract NativeMaster with Deployable {
    total_supply: Int as coins = 0;
    mintable: Bool = true;
    owner: Address;
    jetton_content: Cell;

    receive(msg: Mint) { // 0xfc708bd2
        let ctx: Context = context();
        require(ctx.sender == self.owner, "Not owner");
        require(self.mintable, "Not mintable");
        self.mint(msg.receiver, msg.amount, self.owner); // (to, amount, response_destination)
    }

    receive("Mint: 100") { // Public Minting
        let ctx: Context = context();
        require(self.mintable, "Not mintable");
        self.mint(ctx.sender, 100, self.owner); // 🔴 
    }

    fun mint(to: Address, amount: Int, response_destination: Address) {
        require(self.mintable, "Can't Mint Anymore");
        self.total_supply = self.total_supply + amount; // Update total supply

        let winit: StateInit = initOf NativeWallet(to, myAddress()); // Create message
        send(SendParameters{
            to: contractAddress(winit), 
            value: 0, 
            bounce: false,
            mode: SendRemainingValue,
            body: InternalTransfer{ 
                query_id: 0,
                amount: amount,
                from: myAddress(),
                response_destination: response_destination,
                forward_ton_amount: 0,
                forward_payload: beginCell().endCell().asSlice()
            }.toCell(),
            code: winit.code,
            data: winit.data
        });
    }


    init(owner: Address, jetton_content: Cell) {
        self.owner = owner;
        self.jetton_content = jetton_content;
    }

    receive(msg: ChangeContent) {
        require(self.owner == sender(), "Not owner");
        self.jetton_content = msg.jetton_content;
    }

    receive(msg: Transfer) {
        let ctx: Context = context();
        require(ctx.sender == self.owner, "Not owner");
        require(self.mintable, "Mint stopped");
        require(ctx.readForwardFee() * 2 + 2 * gasConsumption + minTons + msg.forward_ton_amount < ctx.value, "Invalid ton amount");
        self.total_supply = self.total_supply + msg.amount;
        let init: StateInit = initOf NativeWallet(msg.destination, myAddress());
        let to: Address = contractAddress(init);

        send(SendParameters {
            to: to,
            value: 0,
            mode: SendRemainingValue,
            bounce: false,
            body: InternalTransfer{
                query_id: msg.query_id,
                amount: msg.amount,
                from: self.owner,
                response_destination: msg.response_destination,
                forward_ton_amount: msg.forward_ton_amount,
                forward_payload: msg.forward_payload}.toCell(),
            data: init.data,
            code: init.code
        });
    }

    receive(msg: ProvideWalletAddress) {
        let ctx: Context = context();
        let wallet: Address = contractAddress(initOf NativeWallet(msg.owner_address, myAddress()));
        let owner_address: Address? = null;
        if (msg.include_address) {
            owner_address = msg.owner_address;
        }
        send(SendParameters {
            to: ctx.sender,
            value: 0,
            mode: SendRemainingValue,
            body: TakeWalletAddress{
                query_id: msg.query_id,
                wallet_address: wallet,
                owner_address: beginCell().storeBool(true).storeAddress(msg.owner_address).endCell().asSlice()
            }.toCell()
        });
    }

    receive("Stop Mint") {
        require(sender() == self.owner, "Not owner");
        self.mintable = false;
    }

    receive(msg: BurnNotification) {
        let init: StateInit = initOf NativeWallet(msg.sender, myAddress());
        require(contractAddress(init) == sender(), "Invalid sender");

        self.total_supply = self.total_supply - msg.amount;
        send(SendParameters{
            to: msg.response_destination,
            value: 0,
            mode: SendRemainingValue,
            body: Excesses{query_id: msg.query_id}.toCell()
        });
    }

    get fun get_jetton_data(): MasterData {
        return MasterData{total_supply: self.total_supply, mintable: self.mintable, owner: self.owner, jetton_content: self.jetton_content, jetton_wallet_code: (initOf NativeWallet(self.owner, myAddress())).code};
    }

    get fun get_wallet_address(owner_address: Address): Address {
        let init: StateInit = initOf NativeWallet(owner_address, myAddress());
        return contractAddress(init);
    }
}